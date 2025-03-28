import json
from collections import Counter

# This function loads a local JSON file containing Bluesky posts,
# and extracts the repost counts from each post.
# It returns a dictionary with repost count values as keys,
# and the number of posts with that count as values (sorted descending).
def extract(min_reposts=0, max_reposts=None, top_n=None):
    with open('data/all_posts_with_hashtags.json') as file:
        json_records = json.load(file)

    reposts = []

    # Loop through each post to collect its repost count
    for json_data in json_records:
        try:
            repost_count = json_data['repost_count']
            if repost_count >= min_reposts and (max_reposts is None or repost_count <= max_reposts):
                reposts.append(repost_count)
        except Exception as error:
            print("Error reading post:", error)
            print(json_data)
            break

    # Count how many posts had each repost value
    reposts_counter = Counter(reposts)
    sorted_counts = dict(sorted(reposts_counter.items(), key=lambda item: item[1], reverse=True))

    if top_n:
        sorted_counts = dict(list(sorted_counts.items())[:top_n])

    return sorted_counts

# Run standalone for testing
if __name__ == '__main__':
    print(extract())
