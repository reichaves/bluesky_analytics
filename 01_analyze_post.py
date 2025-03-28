import re
from collections import Counter
from datetime import datetime

import requests
import pandas as pd

# Base URL for all Bluesky public API requests
BASE_URL = "https://public.api.bsky.app/xrpc"

# Regex pattern to detect country and regional flags in Unicode format
FLAG_REGEX = re.compile(
    r'[\U0001F1E6-\U0001F1FF]{2}|'  # Country flags (two regional indicator symbols)
    r'\U0001F3F4[\U000E0061-\U000E007A]{2,7}\U000E007F'  # Regional flags (🏴 + 2–7 tag letters + terminator)
)

# Converts a Bluesky post URL to its internal URI using the handle and post ID
def url_to_uri(url):
    handle = url.split("/profile/")[1].split("/post/")[0]
    post_id = url.split("/")[-1]
    r = requests.get(f"{BASE_URL}/com.atproto.identity.resolveHandle?handle={handle}")
    if r.ok:
        did = r.json()["did"]
        return f"at://{did}/app.bsky.feed.post/{post_id}"
    else:
        raise ConnectionError("Could not resolve handle")

# Retrieves all likes (with pagination) for a given Bluesky URI
def get_all_likes_public(uri):
    all_likes = []
    cursor = None
    while True:
        url = f"{BASE_URL}/app.bsky.feed.getLikes?uri={uri}"
        if cursor is not None:
            url += f"&cursor={cursor}"
        r = requests.get(url)
        if not r.ok:
            raise ConnectionError("Failed to fetch likes")
        data = r.json()
        all_likes.extend(data["likes"])
        cursor = data.get("cursor")
        if cursor:
            continue
        else:
            break
    return all_likes

def get_embed(url):
    r = requests.get("https://embed.bsky.app/oembed", params = {"url": url})
    if r.ok:
        return r.json()["html"]
    else:
        raise ConnectionError

# def extract(json_records, start_date=None, end_date=None):
#     # with open("data/all_posts_with_hashtags.json") as file:
#     #     json_records = json.load(file)

#     likes_by_date = Counter()
#     skipped = 0
#     processed = 0

#     for json_data in json_records:
#         try:
#             created = json_data.get("record", {}).get("createdAt")
#             if not created:
#                 skipped += 1
#                 continue
#             dt = datetime.strptime(created[:10], "%Y-%m-%d").date()
#             like_count = json_data.get("like_count", 0)

#             if (start_date is None or dt >= start_date) and (end_date is None or dt <= end_date):
#                 likes_by_date[dt] += like_count
#                 processed += 1
#         except Exception as error:
#             print("Error parsing entry:", error)
#             print(json_data)


#     return dict(sorted(likes_by_date.items())), processed, skipped

# Main function to run flag detection logic
# Returns:
# - A Counter of all flags found in display names
# - A list of user profile data with flags found
def run(url, start_date=None, end_date=None):
    uri = url_to_uri(url=url)
    likes = get_all_likes_public(uri)
    embed_html = get_embed(url=url)

    all_flags = []
    profiles = []
    for like in likes:
        actor = like.get("actor", {})
        display_name = actor.get("displayName", "")
        handle = actor.get("handle", "")
        avatar = actor.get("avatar", "")
        created = like.get("createdAt", "")

        # Find all flag emojis in display name
        flags_found = re.findall(FLAG_REGEX, display_name)
        all_flags.extend(flags_found)

        # Build profile record
        profiles.append({
            "displayName": display_name,
            "handle": handle,
            "avatar": avatar,
            "createdAt": created,
            "flags": ", ".join(flags_found) if flags_found else "—"
        })

    # data, processed, skipped = extract(json_records=likes, start_date=start_date, end_date=end_date)
    df = pd.DataFrame([{"Likes": like.get("actor", {}).get("displayName"), "Time": like["createdAt"]} for like in likes])
    df["Time"] = pd.to_datetime(df["Time"])
    time_range = df["Time"].max() - df["Time"].min()
    if time_range > pd.Timedelta(days = 5):
        freq = "D"
    elif time_range > pd.Timedelta(hours = 5):
        freq = "h"
    else:
        freq = "min"
    group = df.groupby(pd.Grouper(freq = freq, key = "Time")).agg("count")

    return Counter(all_flags), profiles, group, embed_html

# Optional CLI usage for testing the script standalone
def main():
    post_url = input("Enter Bluesky post URL: ")
    flag_count, profile_data, data, processe, skipped = run(post_url)
    print("Flag count:", flag_count)
    print("Profiles:", profile_data)

if __name__ == "__main__":
    main()