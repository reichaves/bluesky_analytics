import json
from collections import Counter


def extract():
    with open('user_posts_sample.json') as file:
        json_records = json.load(file)
        file.close()

    output = []

    for json_data in json_records:
        post = json_data['post']

        if 'embed' in post['record'] and post['record']['embed']['$type'] == 'app.bsky.embed.record':

            if 'author' in post['embed']['record']:
                output.append(post['embed']['record']['author']['handle'])

    most_reposted_by_user = Counter(output)
    return dict(sorted(most_reposted_by_user.items(), key=lambda item: item[1], reverse=True))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    extract()

# See PyCharm help at h
