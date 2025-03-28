import json
from collections import Counter
from datetime import datetime

# This function reads a dataset of Bluesky posts and counts how many likes happened on each date
# It returns a dictionary with dates (YYYY-MM-DD) as keys and like counts as values

def extract(start_date=None, end_date=None):
    with open("data/all_posts_with_hashtags.json") as file:
        json_records = json.load(file)

    likes_by_date = Counter()

    for json_data in json_records:
        try:
            created = json_data.get("record", {}).get("createdAt", "")
            dt = datetime.strptime(created[:10], "%Y-%m-%d").date()
            like_count = json_data.get("like_count", 0)

            if (start_date is None or dt >= start_date) and (end_date is None or dt <= end_date):
                likes_by_date[dt] += like_count
        except Exception as error:
            print("Error parsing entry:", error)
            print(json_data)

    return dict(sorted(likes_by_date.items()))

# Standalone test run
if __name__ == '__main__':
    print(extract())
