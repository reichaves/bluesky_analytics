import time
import logging
from collections import Counter
from typing import List, Dict, Tuple

import requests

# ----------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------
BASE_URL = "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts"
DATA_LIMIT = 2_000  # maximum number of posts to retrieve per query
PAGE_SIZE = 100     # API maximum is 100
HEADERS = {
    "User-Agent": "BlueskyAnalytics/0.2 (+https://github.com/your‑org/bluesky‑analytics)"
}
TIMEOUT = 10  # seconds for HTTP requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ----------------------------------------------------------------------------
# API helpers
# ----------------------------------------------------------------------------

def _build_query(hashtag: str) -> str:
    """Return a URL‑encoded query string for the hashtag search."""
    tag = hashtag.lstrip("#")  # remove leading # if present
    return f"%23{tag}"


def search_hashtags(hashtag: str, limit: int = DATA_LIMIT) -> List[Dict]:
    """Fetch *limit* Bluesky posts containing *hashtag*.

    The function paginates through the public Bluesky API. It respects HTTP 429
    (rate‑limit) responses by waiting for the server‑specified *Retry‑After*
    value (or 1 second if missing) before retrying the same request.
    """

    if not hashtag:
        raise ValueError("hashtag must be a non‑empty string")

    query = _build_query(hashtag)
    cursor = None
    posts: List[Dict] = []

    remaining = max(0, limit)
    backoff = 1  # exponential back‑off base in seconds

    while remaining > 0:
        params = {
            "q": query,
            "limit": min(PAGE_SIZE, remaining),
        }
        if cursor:
            params["cursor"] = cursor

        try:
            resp = requests.get(
                BASE_URL,
                params=params,
                headers=HEADERS,
                timeout=TIMEOUT,
            )
        except requests.RequestException as exc:
            logger.error("network error when calling Bluesky API", exc_info=exc)
            raise

        # handle rate limiting ------------------------------------------------
        if resp.status_code == 429:
            retry_after = int(resp.headers.get("Retry-After", backoff))
            logger.warning("hit rate limit – sleeping %s s", retry_after)
            time.sleep(retry_after)
            backoff = min(backoff * 2, 60)  # cap exponential back‑off at 60 s
            continue  # retry same request

        # raise for other HTTP errors ----------------------------------------
        resp.raise_for_status()

        data = resp.json()
        posts.extend(data.get("posts", []))

        cursor = data.get("cursor")
        if not cursor:
            break  # no more pages

        remaining = limit - len(posts)

    logger.info("fetched %d posts containing %s", len(posts), hashtag)
    return posts[:limit]

# ----------------------------------------------------------------------------
# Feature extraction helpers
# ----------------------------------------------------------------------------

def extract(
    hashtag: str,
    min_count: int = 1,
    max_count: int | None = None,
    top_n: int | None = None,
) -> Tuple[Dict[str, int], List[Tuple[str, str]]]:
    """Return hashtag co‑occurrence frequencies and the most active users.

    Parameters
    ----------
    hashtag : str
        The hashtag to search for.
    min_count : int, optional
        Minimum frequency for a hashtag to be kept in the result.
    max_count : int | None, optional
        Maximum frequency; pass *None* for no upper bound.
    top_n : int | None, optional
        If provided, only the *top_n* most frequent hashtags are returned.

    Returns
    -------
    counts : dict[str, int]
        Dictionary of related hashtags → frequency, sorted descending.
    top_users : list[tuple[str, str]]
        List of (handle, displayName) tuples for the top 10 posters.
    """

    json_records = search_hashtags(hashtag)

    hashtags: List[str] = []

    for post in json_records:
        try:
            facets = post["record"].get("facets", [])
            for facet in facets:
                feature = facet.get("features", [{}])[0]
                tag = feature.get("tag")
                if tag:
                    hashtags.append(tag.lower())
        except Exception as err:  # noqa: BLE001
            logger.debug("error reading post: %s", err, exc_info=err)
            logger.debug(post)

    # count occurrences ------------------------------------------------------
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
        (post["author"]["handle"], post["author"].get("displayName", ""))
        for post in json_records
    ).most_common(10)

    return sorted_filtered, top_users

# ----------------------------------------------------------------------------
# CLI for quick tests
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    import pprint

    logging.basicConfig(level=logging.INFO)
    pprint.pp(extract("#bluesky"))



# See PyCharm help at https://www.jetbrains.com/help/pycharm/
