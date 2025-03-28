from collections import Counter

import requests

BASE_URL = "https://public.api.bsky.app/xrpc"

DATA_LIMIT = 2000

def handle_to_did(handle):
    r = requests.get(f"{BASE_URL}/com.atproto.identity.resolveHandle?handle={handle}")
    if r.ok:
        return r.json()["did"]
    else:
        raise ConnectionError

def get_user_posts(handle):
    if "bsky.app/" in handle:
        handle = handle.strip("/").split("/")[-1]
    if handle.startswith("@"):
        handle = handle[1:]
    if "." not in handle:
        handle = handle + ".bsky.social"

    did = handle_to_did(handle = handle)
    all_posts = []
    cursor = None
    url = f"{BASE_URL}/app.bsky.feed.getAuthorFeed"
    params = {
        "actor": did,
        "limit": 100
    }

    while True:
        if len(all_posts) > DATA_LIMIT:
            break
        if cursor:
            params.update({"cursor": cursor})
        r = requests.get(url, params = params)
        if not r.ok:
            raise ConnectionError
        data = r.json()
        all_posts.extend(data["feed"])
        cursor = data.get("cursor")
        if cursor:
            continue
        else:
            break

    return all_posts

def extract(json_records):

    output = []

    for json_data in json_records:
        post = json_data['post']

        if 'embed' in post['record'] and post['record']['embed']['$type'] == 'app.bsky.embed.record':

            if 'author' in post['embed']['record']:
                if "handle" not in post['embed']['record']['author'].keys():
                    continue
                output.append(post['embed']['record']['author']['handle'])

    most_reposted_by_user = Counter(output)
    return dict(sorted(most_reposted_by_user.items(), key=lambda item: item[1], reverse=True))

def extract_most_replied_to(json_records):

    output = []

    for json_data in json_records:
        post = json_data['post']

        if 'reply' in json_data:
            output.append(post['author']['handle'])

    total_replies_by_user = Counter(output)
    sorted_total_replies_by_user = dict(sorted(total_replies_by_user.items(), key=lambda item: item[1], reverse=True))

    return sorted_total_replies_by_user

def run(handle):
    posts = get_user_posts(handle = handle)
    return extract(json_records=posts), extract_most_replied_to(json_records=posts)

if __name__ == "__main__":
    handle = "tristanl.ee"
    posts = get_user_posts(handle = handle)
    print(extract(posts))