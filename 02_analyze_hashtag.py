import time
import logging
from collections import Counter
from typing import List, Dict, Tuple

import requests

# ----------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------
BASE_URL = "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts"
DATA_LIMIT = 2_000  # total posts to pull
PAGE_SIZE = 80      # <100 seems to avoid some 403 responses
HEADERS = {
    "User-Agent": "BlueskyAnalytics/0.2",
    "Accept": "application/json",
}
TIMEOUT = 10  # seconds
MAX_RETRIES = 4  # attempts per page when we hit 403/429

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ----------------------------------------------------------------------------
# API helpers
# ----------------------------------------------------------------------------

def _build_query(hashtag: str) -> str:
    tag = hashtag.lstrip("#")
    return f"#{tag}"


def _request_with_backoff(params: dict) -> dict:
    """Internal helper that performs GET with exponential back‑off.

    Retries on 403 (often proxy‑rate‑limit) and 429 (explicit rate‑limit).
    """
    attempt = 0
    backoff = 1
    while attempt < MAX_RETRIES:
        resp = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=TIMEOUT)
        if resp.status_code in (403, 429):
            # treat both as temporary throttle from the AppView proxy
            wait = int(resp.headers.get("Retry-After", backoff))
            logger.warning("%s returned – sleeping %s s (attempt %s)", resp.status_code, wait, attempt + 1)
            time.sleep(wait)
            backoff = min(backoff * 2, 60)
            attempt += 1
            continue
        resp.raise_for_status()
        return resp.json()
    # if we exhausted retries
    resp.raise_for_status()  # will raise HTTPError with last response


def search_hashtags(hashtag: str, limit: int = DATA_LIMIT) -> List[Dict]:
    if not hashtag:
        raise ValueError("hashtag must be non‑empty")

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

        data = _request_with_backoff(params)
        posts.extend(data.get("posts", []))
        cursor = data.get("cursor")
        if not cursor:
            break
        remaining = limit - len(posts)

    logger.info("fetched %d posts for %s", len(posts), hashtag)
    return posts[:limit]

# ----------------------------------------------------------------------------
# Feature extraction
# ----------------------------------------------------------------------------

def extract(
    hashtag: str,
    min_count: int = 1,
    max_count: int | None = None,
    top_n: int | None = None,
) -> Tuple[Dict[str, int], List[Tuple[str, str]]]:
    json_records = search_hashtags(hashtag)
    hashtags: List[str] = []

    for post in json_records:
        facets = post.get("record", {}).get("facets", [])
        for facet in facets:
            tag = facet.get("features", [{}])[0].get("tag")
            if tag:
                hashtags.append(tag.lower())

    counter: Counter[str] = Counter(hashtags)
    filtered = {
        tag: cnt
        for tag, cnt in counter.items()
        if cnt >= min_count and (max_count is None or cnt <= max_count)
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
    import pprint, sys, logging as lg
    lg.basicConfig(level=lg.INFO)
    hashtag = sys.argv[1] if len(sys.argv) > 1 else "#bluesky"
    pprint.pp(extract(hashtag))
