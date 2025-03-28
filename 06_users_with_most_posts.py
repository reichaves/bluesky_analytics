import json
from collections import Counter

def extract():
    with open('user_posts_sample.json') as file:
        json_records = json.load(file)
        file.close()

    output = []

    for json_data in json_records:
        post = json_data['post']

        if 'reply' not in json_data:
            output.append(post['author']['handle'])

        if 'embed' in post['record'] and post['record']['embed']['$type'] == 'app.bsky.embed.record':

            if 'author' in post['embed']['record']:
                output.append(post['embed']['record']['author']['handle'])

    users_with_most_posts = Counter(output)
    return dict(sorted(users_with_most_posts.items(), key=lambda item: item[1], reverse=True))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    extract()
