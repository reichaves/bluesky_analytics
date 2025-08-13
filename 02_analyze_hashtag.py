import time
import logging
from collections import Counter
from typing import List, Dict, Tuple, Optional
import random

import requests

# ----------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------
PRIMARY_URL = "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts"
FALLBACK_URL = "https://search.bsky.social/search/posts"
# Adicionando mais endpoints alternativos
ALTERNATIVE_ENDPOINTS = [
    "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts",
    "https://bsky.social/xrpc/app.bsky.feed.searchPosts",
    "https://api.bsky.app/xrpc/app.bsky.feed.searchPosts"
]

DATA_LIMIT = 2_000
PAGE_SIZE = 25  # Reduzido para evitar rate limiting
HEADERS = {
    "User-Agent": "BlueskyAnalytics/0.4",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache"
}
TIMEOUT = 15
MAX_RETRIES = 2  # Reduzido para acelerar fallbacks
RATE_LIMIT_DELAY = 2  # Delay base entre requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------

def _build_query(hashtag: str) -> str:
    """Constrói query mais robusta para hashtags"""
    tag = hashtag.lstrip("#")
    # Tenta diferentes formatos de query
    return f"#{tag}"

def _get_random_user_agent():
    """Retorna um User-Agent aleatório para evitar bloqueios"""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        "BlueskyAnalytics/0.4",
        "curl/7.68.0",
        "PostmanRuntime/7.28.0"
    ]
    return random.choice(user_agents)

def _query_endpoint(url: str, params: dict, headers: Optional[dict] = None) -> requests.Response:
    """HTTP GET com headers rotativos e melhor error handling"""
    if headers is None:
        headers = HEADERS.copy()
        headers["User-Agent"] = _get_random_user_agent()
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=TIMEOUT)
        return response
    except requests.exceptions.Timeout:
        logger.warning(f"Timeout for {url}")
        raise
    except requests.exceptions.ConnectionError:
        logger.warning(f"Connection error for {url}")
        raise

def _fetch_page_with_fallback(params: dict) -> dict:
    """Tenta múltiplos endpoints com fallback inteligente"""
    
    # Lista de endpoints para tentar
    endpoints_to_try = ALTERNATIVE_ENDPOINTS + [FALLBACK_URL]
    
    for endpoint_idx, base_url in enumerate(endpoints_to_try):
        logger.info(f"Tentando endpoint {endpoint_idx + 1}/{len(endpoints_to_try)}: {base_url}")
        
        for attempt in range(MAX_RETRIES):
            try:
                # Adiciona delay entre requests para evitar rate limiting
                if attempt > 0 or endpoint_idx > 0:
                    delay = RATE_LIMIT_DELAY * (2 ** attempt) + random.uniform(0.5, 1.5)
                    logger.info(f"Aguardando {delay:.1f}s antes da tentativa...")
                    time.sleep(delay)
                
                response = _query_endpoint(base_url, params)
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Sucesso com {base_url}")
                    return data
                elif response.status_code in (403, 429):
                    retry_after = int(response.headers.get("Retry-After", RATE_LIMIT_DELAY * (2 ** attempt)))
                    logger.warning(f"Rate limit {response.status_code} em {base_url} - tentativa {attempt + 1}/{MAX_RETRIES}")
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(retry_after)
                        continue
                    else:
                        break  # Tenta próximo endpoint
                elif response.status_code == 404:
                    logger.warning(f"Endpoint {base_url} não encontrado (404)")
                    break  # Tenta próximo endpoint
                else:
                    logger.warning(f"HTTP {response.status_code} de {base_url}: {response.text[:200]}")
                    break  # Tenta próximo endpoint
                    
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                logger.warning(f"Erro de conexão com {base_url}: {str(e)}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RATE_LIMIT_DELAY)
                    continue
                else:
                    break  # Tenta próximo endpoint
    
    # Se chegou aqui, todos os endpoints falharam
    raise ConnectionError("Todos os endpoints da API Bluesky falharam. Tente novamente mais tarde.")

def search_hashtags(hashtag: str, limit: int = DATA_LIMIT) -> List[Dict]:
    """Busca hashtags com fallback robusto e rate limiting"""
    if not hashtag:
        raise ValueError("hashtag é obrigatório")

    posts: List[Dict] = []
    cursor = None
    remaining = max(0, limit)
    page_count = 0
    max_pages = 50  # Limite de páginas para evitar loops infinitos

    logger.info(f"Iniciando busca por hashtag: {hashtag}")

    while remaining > 0 and page_count < max_pages:
        params = {
            "q": _build_query(hashtag),
            "limit": min(PAGE_SIZE, remaining),
        }
        if cursor:
            params["cursor"] = cursor

        try:
            data = _fetch_page_with_fallback(params)
            new_posts = data.get("posts", [])
            
            if not new_posts:
                logger.info("Nenhum post encontrado, encerrando busca")
                break
                
            posts.extend(new_posts)
            cursor = data.get("cursor") or data.get("nextPageCursor")
            
            page_count += 1
            remaining = limit - len(posts)
            
            logger.info(f"Página {page_count}: {len(new_posts)} posts coletados, total: {len(posts)}")
            
            if not cursor:
                logger.info("Sem mais páginas disponíveis")
                break
                
        except ConnectionError as e:
            logger.error(f"Falha na conexão: {str(e)}")
            # Se já temos alguns posts, retorna o que conseguimos
            if posts:
                logger.info(f"Retornando {len(posts)} posts coletados antes da falha")
                break
            else:
                raise

    logger.info(f"Busca concluída: {len(posts)} posts coletados para #{hashtag}")
    return posts[:limit]

# ----------------------------------------------------------------------------
# extraction com tratamento de erros melhorado
# ----------------------------------------------------------------------------

def extract(
    hashtag: str,
    min_count: int = 1,
    max_count: int | None = None,
    top_n: int | None = None,
) -> Tuple[Dict[str, int], List[Tuple[str, str]]]:
    """Extrai hashtags e usuários com melhor tratamento de erros"""
    try:
        json_records = search_hashtags(hashtag)
        
        if not json_records:
            logger.warning(f"Nenhum post encontrado para hashtag #{hashtag}")
            return {}, []
            
    except ConnectionError as err:
        error_msg = f"Não foi possível acessar a API do Bluesky para a hashtag #{hashtag}. " \
                   f"Isso pode ser devido a rate limiting ou bloqueios temporários. " \
                   f"Tente novamente em alguns minutos."
        raise PermissionError(error_msg) from err
    except Exception as err:
        error_msg = f"Erro inesperado ao buscar hashtag #{hashtag}: {str(err)}"
        raise RuntimeError(error_msg) from err

    # Extração de hashtags
    hashtags: List[str] = []
    for post in json_records:
        try:
            facets = post.get("record", {}).get("facets", [])
            for facet in facets:
                features = facet.get("features", [])
                for feature in features:
                    tag = feature.get("tag")
                    if tag:
                        hashtags.append(tag.lower())
        except Exception as e:
            logger.warning(f"Erro ao processar facets do post: {e}")
            continue

    # Contagem e filtragem
    counter: Counter[str] = Counter(hashtags)
    filtered = {
        t: c for t, c in counter.items() 
        if c >= min_count and (max_count is None or c <= max_count)
    }
    sorted_filtered = dict(sorted(filtered.items(), key=lambda kv: kv[1], reverse=True))
    
    if top_n is not None:
        sorted_filtered = dict(list(sorted_filtered.items())[:top_n])

    # Top usuários
    try:
        top_users = Counter(
            (p["author"]["handle"], p["author"].get("displayName", "")) 
            for p in json_records 
            if "author" in p and "handle" in p["author"]
        ).most_common(10)
    except Exception as e:
        logger.warning(f"Erro ao processar usuários: {e}")
        top_users = []

    return sorted_filtered, top_users

# ----------------------------------------------------------------------------
# Função de teste
# ----------------------------------------------------------------------------
def test_connection():
    """Testa conectividade com os endpoints"""
    test_hashtag = "bluesky"
    logger.info("Testando conectividade com APIs...")
    
    for i, endpoint in enumerate(ALTERNATIVE_ENDPOINTS):
        try:
            params = {"q": f"#{test_hashtag}", "limit": 1}
            response = _query_endpoint(endpoint, params)
            logger.info(f"Endpoint {i+1}: {endpoint} - Status: {response.status_code}")
        except Exception as e:
            logger.info(f"Endpoint {i+1}: {endpoint} - Erro: {str(e)}")

if __name__ == "__main__":
    import pprint, sys
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_connection()
    else:
        tag = sys.argv[1] if len(sys.argv) > 1 else "bluesky"
        try:
            result = extract(tag)
            pprint.pp(result)
        except Exception as e:
            logger.error(f"Falha na execução: {str(e)}")
