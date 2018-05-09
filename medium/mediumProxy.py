import csv
import json
import click
import requests
from time import sleep
from datetime import datetime, timedelta

proxies = {
    'http': "socks5://127.0.0.1:1080",
    'https': "socks5://127.0.0.1:1080",
}

# the base URL
MEDIUM = 'https://medium.com'

# clean ])}while(1);</x> up and turn the JSON into a Python dictionary.
def cleanJson(response):
    return json.loads(response.text.replace('])}while(1);</x>', '', 1))

# Pull the userId from a given username
# Then query the /_/api/users/<user_id>/following endpoint
# get the list of usernames from the following list
def fetchAUserIdByInput(username):
    print('Retrieving user ID...')

    url = MEDIUM + '/@' + username + '?format=json'
    response = requests.get(url, proxies=proxies)
    responseDict = cleanJson(response)

    return responseDict['payload']['user']['userId']

# pagination / limit / to
# a loop to get all the usernames from the following list
def fetchFollowingUsernamesBy(userId):
    print('Retrieving usernames from Following List...')

    nextTo = False
    following = []

    while True:

        if nextTo:
            # If this is not the first page of the followings list
            url = MEDIUM + '/_/api/users/' + userId + '/following?limit=8&to=' + nextTo
        else:
            # If this is the first page of the followings list
            url = MEDIUM + '/_/api/users/' + userId + '/following'

        response = requests.get(url, proxies=proxies)
        responseDict = cleanJson(response)
        payload = responseDict['payload']

        for user in payload['value']:
            following.append(user['username'])

        try:
            # If the "to" key is missing, we've reached the end
            # of the list and an exception is thrown
            nextTo = payload['paging']['next']['to']
        except:
            break

    return following

# get the latest posts(post_ids) from each user by all the usernames
def fetchLatestPostIdsBy(usernames):
    print('Retrieving the latest posts...')

    postIds = []
    for username in usernames:
        url = MEDIUM + '/@' + username + '/latest?format=json'
        response = requests.get(url, proxies=proxies)
        responseDict = cleanJson(response)

        try:
            posts = responseDict['payload']['references']['Post']
        except:
            posts = []

        if posts:
            # posts.keys()
            for key in posts.keys():
                postIds.append(posts[key]['id'])

    return postIds

# get all the responses from each post by post_ids
def fetchResponsesOfEachPostBy(postIds):
    print('Retrieving the post responses...')

    responses = []
    for postId in postIds:
        url = MEDIUM + '/_/api/posts/' + postId + '/responses'
        response = requests.get(url, proxies=proxies)
        responseDict = cleanJson(response)
        responses += responseDict['payload']['value']
        sleep(0.5) # This is the most intensive operation for the Medium servers

    return responses

# Filter the responses
# Checks if a response was created in the last 30 days (recent responses)
def isRecent(response):
    limitDate = datetime.now() - timedelta(days=30)
    createdAt = response['createdAt'] / 1000
    createDate = datetime.fromtimestamp(createdAt)

    if createDate >= limitDate:
        return True

# Checks if a response is over a certain number of recommends
def isHighRecommend(response, recommend_min):
    if response['virtuals']['recommends'] >= recommend_min:
        return True


# get each response and its author's userIds and usernames
def fetchAllUserIdsFrom(responses, recommend_min):
    print('Retrieving user IDs from the responses...')

    userIds = []
    for response in responses:
        recent = isRecent(response)
        highRecommends = isHighRecommend(response, recommend_min)

        if recent and highRecommends:
            userIds.append(response['creatorId'])

    return userIds

def fetchUsernamesBy(userIds):
    print('Retrieving usernames of interesting users...')

    usernames = []
    for userId in userIds:
        url = MEDIUM + '/_/api/users/' + userId
        response = requests.get(url, proxies=proxies)
        responseDict = cleanJson(response)
        payload = responseDict['payload']
        usernames.append(payload['value']['username'])

    return usernames

# Add list of interesting users to the interesting_users.csv and add a timestamp
def storeToCsv(interestingUsers):
    with open('interestingUsers.csv', 'a') as file:
        writer = csv.writer(file)

        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        interestingUsers.insert(0, now)
        writer.writerow(interestingUsers)

# put them together
def fetchFollowingInterestingUsersBy(username, recommend_min):
    print('Looking for interesting users for %s...' % username)

    userId = fetchAUserIdByInput(username)
    usernames = fetchFollowingUsernamesBy(userId)
    postIds = fetchLatestPostIdsBy(usernames)
    responses = fetchResponsesOfEachPostBy(postIds)
    userIds = fetchAllUserIdsFrom(responses, recommend_min)

    return fetchUsernamesBy(userIds)

@click.command()
@click.option('-n', '--name', default='explorewo', help='Medium username')
@click.option('-r', '--min-recommendations', default=10, help='Minimum number of recommendations per response')

def main(name, min_recommendations):
    interestingUsers = fetchFollowingInterestingUsersBy(name, min_recommendations)
    print(interestingUsers)
    storeToCsv(interestingUsers)

if __name__ == '__main__':
    main()
