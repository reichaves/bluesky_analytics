import json
from collections import Counter

import requests

BASE_URL = "https://public.api.bsky.app/xrpc"
DATA_LIMIT = 2000

def search_hashtags(hashtag):
    """Behavior may be unreliable in future: https://github.com/bluesky-social/atproto/issues/3583#issuecomment-2704441168"""
    all_posts = []
    cursor = None
    if not hashtag.startswith("#"):
        hashtag = "#" + hashtag
    parameters = {
        "q": hashtag,
        "limit": 100
    }
    url = f"{BASE_URL}/app.bsky.feed.searchposts"
    all_posts = []
    while True:
        if len(all_posts) > DATA_LIMIT:
            break
        if cursor:
            parameters.update({"cursor": cursor})
        r = requests.get(url, params = parameters)
        if not r.ok:
            raise ConnectionError
        data = r.json()
        all_posts.extend(data["posts"])
        cursor = data.get("cursor")
        if cursor:
            continue
        else:
            break

    return all_posts

# This function loads a local JSON file of Bluesky posts
# and extracts hashtags from the 'facets' field of each post.
# It returns a dictionary with hashtag frequencies (sorted descending),
# with optional filters for minimum count, maximum count, and top N hashtags.
def extract(hashtag, min_count=1, max_count=None, top_n=None):

    json_records = search_hashtags(hashtag=hashtag)

    hashtags = []

    # Loop through each post in the dataset
    for json_data in json_records:
        try:
            facets = json_data['record']['facets']

            # Look for tags inside each facet (if present)
            for facet in facets:
                if 'tag' in facet['features'][0]:
                    hashtags.append(facet['features'][0]['tag'].lower())

        except Exception as error:
            print("Error reading post:", error)
            print(json_data)

    # Count and optionally filter hashtags
    hashtag_counter = Counter(hashtags)

    filtered = {
        tag: count for tag, count in hashtag_counter.items()
        if count >= min_count and (max_count is None or count <= max_count)
    }

    sorted_filtered = dict(
        sorted(filtered.items(), key=lambda item: item[1], reverse=True)
    )

    if top_n:
        sorted_filtered = dict(list(sorted_filtered.items())[:top_n])

    return sorted_filtered

# Run standalone for debugging
if __name__ == '__main__':
    print(extract())


# See PyCharm help at https://www.jetbrains.com/help/pycharm/