import csv
import json
import click
import requests
from time import sleep
from datetime import datetime, timedelta

# the base URL
MEDIUM = 'https://medium.com'

proxies = {
    'http': "socks5://127.0.0.1:1080",
    'https': "socks5://127.0.0.1:1080",
}

def get_response(url):
    return requests.get(url, proxies=proxies)

# clean ])}while(1);</x> up and turn the JSON into a Python dictionary.
def clean_json_from(response):
    return json.loads(response.text.replace('])}while(1);</x>', '', 1))

# Pull the user ID from a given username
# Then query the /_/api/users/<user_id>/following endpoint
# get the list of usernames from the following list
def fetch_user_id_by(username):
    print('Retrieving user ID...')

    url = MEDIUM + '/@' + username + '?format=json'
    response = get_response(url)
    response_dict = clean_json_from(response)
    user_id = response_dict['payload']['user']['userId']

    return user_id

# pagination / limit / to
# a loop
def fetch_following_usernames_by(user_id):
    print('Retrieving usernames from Followings...')

    next_id = False
    usernames = []

    while True:
        if next_id:
            # If this is not the first page of the followings list
            url = MEDIUM + '/_/api/users/' + user_id + '/following?limit=8&to=' + next_id
        else:
            # If this is the first page of the followings list
            url = MEDIUM + '/_/api/users/' + user_id + '/following'

        response = get_response(url)
        response_dict = clean_json_from(response)
        payload = response_dict['payload']

        for user in payload['value']:
            usernames.append(user['username'])

        try:
            # If the "to" key is missing, we've reached the end
            # of the list and an exception is thrown
            next_id = payload['paging']['next']['to']
        except:
            break

    return usernames

# take a list of usernames
# return a list of post IDs for the latest posts
def fetch_latest_post_ids_by(usernames):
    print('Retrieving the latest posts...')

    post_ids = []
    for username in usernames:
        url = MEDIUM + '/@' + username + '/latest?format=json'
        response = get_response(url)
        response_dict = clean_json_from(response)

        try:
            posts = response_dict['payload']['references']['Post']
        except:
            posts = []

        if posts:
            for key in posts.keys():
                post_ids.append(posts[key]['id'])

    return post_ids
# https://medium.com/@<username>/latest?format=json

# takes a list of post IDs and returns a list of post responses
def fetch_responses_of_each_post_by(post_ids):
    print('Retrieving the post responses...')

    responses = []
    for post_id in post_ids:
        url = MEDIUM + '/_/api/posts/' + post_id + '/responses'
        response = get_response(url)
        response_dict = clean_json_from(response)
        responses += response_dict['payload']['value']
        sleep(0.5) # This is the most intensive operation for the Medium servers

    return responses
#https://medium.com/_/api/posts/d23dd6b6f08b/responses

# Filtering the responses
# Checks if a response is over a certain number of recommends
def is_high_recommend(response, recommend_min):
    if response['virtuals']['recommends'] >= recommend_min:
        return True

# Checks if a response was created in the last 30 days
def is_recent(response):
    limit_date = datetime.now() - timedelta(days=30)
    creation_epoch_time = response['createdAt'] / 1000
    creation_date = datetime.fromtimestamp(creation_epoch_time)

    if creation_date >= limit_date:
        return True

# get the username of the author of each response
def fetch_user_ids_from(responses, recommend_min):
    print('Retrieving user IDs from the responses...')

    user_ids = []
    for response in responses:
        recent = is_recent(response)
        high = is_high_recommend(response, recommend_min)

        if recent and high:
            user_ids.append(response['creatorId'])

    return user_ids

def fetch_usernames_by(user_ids):
    print('Retrieving usernames of interesting users...')

    usernames = []
    for user_id in user_ids:
        url = MEDIUM + '/_/api/users/' + user_id
        response = requests.get(url)
        response_dict = clean_json_from(response)
        payload = response_dict['payload']
        usernames.append(payload['value']['username'])

    return usernames

# Add list of interesting users to the interesting_users.csv and add a timestamp
def store_to_csv(interesting_users_list):
    with open('interesting_users.csv', 'a') as file:
        writer = csv.writer(file)
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        interesting_users_list.insert(0, now)
        writer.writerow(interesting_users_list)

# put them all together
def fetch_interesting_users_by(username, recommend_min):
    print('Looking for interesting users for %s...' % username)

    user_id = fetch_user_id_by(username)
    following_usernames = fetch_following_usernames_by(user_id)
    post_ids = fetch_latest_post_ids_by(following_usernames)
    post_responses = fetch_responses_of_each_post_by(post_ids)
    user_ids = fetch_user_ids_from(post_responses， recommend_min)

    return fetch_usernames_by(user_ids)

@click.command()
@click.option('-n', '--name', default='explorewo', help='Medium username')
@click.option('-r', '--min-recommendations', default=10, help='Minimum number of recommendations per response')

def main(name, min_recommendations):
    interesting_users = fetch_interesting_users_by(name, min_recommendations)
    print(interesting_users)
    store_to_csv(interesting_users)

if __name__ == '__main__':
    main()
