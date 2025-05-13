import time
import logging
from collections import Counter
from typing import List, Dict, Tuple

import requests

# ----------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------
PRIMARY_URL = "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts"
FALLBACK_URL = "https://search.bsky.social/search/posts"  # unofficial but public
DATA_LIMIT = 2_000
PAGE_SIZE = 60  # conservative to minimise 403
HEADERS = {
    "User-Agent": "BlueskyAnalytics/0.3",
    "Accept": "application/json",
}
TIMEOUT = 10
MAX_RETRIES = 3  # per endpoint

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------

def _build_query(hashtag: str) -> str:
    tag = hashtag.lstrip("#")
    return f"#{tag}"


def _query_endpoint(url: str, params: dict) -> requests.Response:
    """single HTTP GET with basic error handling"""
    return requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)


def _fetch_page(params: dict) -> dict:
    """Try primary endpoint; fall back to search.bsky.social if repeated 403/429."""

    for base in (PRIMARY_URL, FALLBACK_URL):
        attempt, backoff = 0, 1
        while attempt < MAX_RETRIES:
            r = _query_endpoint(base, params)
            if r.status_code in (403, 429):
                wait = int(r.headers.get("Retry-After", backoff))
                logger.warning("%s on %s – sleep %s s (attempt %s)", r.status_code, base, wait, attempt + 1)
                time.sleep(wait)
                backoff = min(backoff * 2, 60)
                attempt += 1
                continue
            if r.ok:
                return r.json()
            # any other HTTP error → break to switch endpoint or raise later
            logger.debug("HTTP %s from %s", r.status_code, base)
            break  # try next base or raise
        # exhausted retries for this base → try next base
    # if we reach here, both endpoints failed
    r.raise_for_status()


def search_hashtags(hashtag: str, limit: int = DATA_LIMIT) -> List[Dict]:
    if not hashtag:
        raise ValueError("hashtag is required")

    posts: List[Dict] = []
    cursor = None
    remaining = max(0, limit)

    while remaining > 0:
        params = {
            "q": _build_query(hashtag),
            "limit": min(PAGE_SIZE, remaining),
        }
        if cursor:
            params["cursor"] = cursor

        data = _fetch_page(params)
        posts.extend(data.get("posts", []))
        cursor = data.get("cursor") or data.get("nextPageCursor")  # fallback API uses nextPageCursor
        if not cursor:
            break
        remaining = limit - len(posts)

    logger.info("%d posts collected for %s", len(posts), hashtag)
    return posts[:limit]

# ----------------------------------------------------------------------------
# extraction
# ----------------------------------------------------------------------------

def extract(
    hashtag: str,
    min_count: int = 1,
    max_count: int | None = None,
    top_n: int | None = None,
) -> Tuple[Dict[str, int], List[Tuple[str, str]]]:
    try:
        json_records = search_hashtags(hashtag)
    except requests.HTTPError as err:
        # propagate a clean error message to Streamlit caller
        raise PermissionError(f"public Bluesky search blocked this term ({err.response.status_code}).") from err

    hashtags: List[str] = []
    for post in json_records:
        for facet in post.get("record", {}).get("facets", []):
            tag = facet.get("features", [{}])[0].get("tag")
            if tag:
                hashtags.append(tag.lower())

    counter: Counter[str] = Counter(hashtags)
    filtered = {
        t: c for t, c in counter.items() if c >= min_count and (max_count is None or c <= max_count)
    }
    sorted_filtered = dict(sorted(filtered.items(), key=lambda kv: kv[1], reverse=True))
    if top_n is not None:
        sorted_filtered = dict(list(sorted_filtered.items())[:top_n])

    top_users = Counter(
        (p["author"]["handle"], p["author"].get("displayName", "")) for p in json_records
    ).most_common(10)

    return sorted_filtered, top_users

# ----------------------------------------------------------------------------
if __name__ == "__main__":
    import pprint, sys
    logging.basicConfig(level=logging.INFO)
    tag = sys.argv[1] if len(sys.argv) > 1 else "#bluesky"
    pprint.pp(extract(tag))
