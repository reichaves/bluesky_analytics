import json
from collections import Counter
from datetime import datetime

# This function reads a dataset of Bluesky posts and counts how many likes happened on each date.
# It returns a dictionary with dates (YYYY-MM-DD) as keys and total like counts as values.

def extract():
    with open("data/all_posts_with_hashtags.json") as file:
        json_records = json.load(file)

    likes_by_date = Counter()

    # Iterate over each post to extract the date and like count
    for json_data in json_records:
        try:
            created = json_data.get("record", {}).get("createdAt", "")
            dt = datetime.strptime(created[:10], "%Y-%m-%d")
            like_count = json_data.get("like_count", 0)
            likes_by_date[dt.date()] += like_count
        except Exception as error:
            print("Error parsing entry:", error)
            print(json_data)

    # Return a dictionary sorted by date
    return dict(sorted(likes_by_date.items()))

# Standalone test run
if __name__ == '__main__':
    print(extract())

