import re
from collections import Counter
import requests

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

# Main function to run flag detection logic
# Returns:
# - A Counter of all flags found in display names
# - A list of user profile data with flags found
def run(url):
    uri = url_to_uri(url=url)
    likes = get_all_likes_public(uri)

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

    return Counter(all_flags), profiles

# Optional CLI usage for testing the script standalone
def main():
    post_url = input("Enter Bluesky post URL: ")
    flag_count, profile_data = run(post_url)
    print("Flag count:", flag_count)
    print("Profiles:", profile_data)

if __name__ == "__main__":
    main()