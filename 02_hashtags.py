import json
from collections import Counter

# This function loads a local JSON file of Bluesky posts
# and extracts hashtags from the 'facets' field of each post.
# It returns a dictionary with hashtag frequencies (sorted descending),
# with optional filters for minimum count, maximum count, and top N hashtags.
def extract(min_count=1, max_count=None, top_n=None):
    with open('data/all_posts_with_hashtags.json') as file:
        json_records = json.load(file)

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