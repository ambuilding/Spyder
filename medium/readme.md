## Find interesting users on Medium

- Interesting users are someone who is
  - from your network
  - active
  - writes responses that are generally apreciated by the Medium community.

- Look through the latest posts from users I follow to see
  - who has responded to those users.
- If they responded to someone I'm following, they must have similar interests to mine.


- API endpoint

	```
	https://medium.com/_/api/users/<userId>
	User: userId / name/ username / twitterScreenName / facebookAccountId
	https://medium.com/_/api/users/<userId>/profile
	userMeta: interestTags / authorTags
	https://medium.com/_/api/users/<userId>/following
	payload / value /

	JSON response
	Except for a string of characters at the beginning of the response
	])}while(1);</x>

	5a2e47aa48be
	```

- get all the users from the following list
  - write a function to pull the user ID from a given username
	- https://medium.com/@<username>?format=json
    - get the latest posts from each user
	- payload /references / Post

	```
	find the URL for JSON feed by ?format=json / get userId
	Pull the userId from a given username
	Query the endpoint / userId

	# pagination
	?limit=8&to=<next_id>

	get all the responses from each post
	https://medium.com/_/api/posts/<post_id>/responses
    ```

- Get the latest posts of each user
  - https://medium.com/@<username>/latest?format=json

- Get all the responses from each post
- Filter the responses
  - Filter out responses that are older than 30 days
  - Filter out responses that have less than a minimum number of recommendations
  - by the number of recommendatins
  - It measures the same thing as claps, but it doesn't take duplicates into account.

	response = / payload / value /
	response / createdAt
	response / virtuals / recommends
	response / creatorId


- get the username(author) of each response

	https://medium.com/_/api/posts/90180824ee3c/responses
	https://medium.com/_/api/posts/81f48b52875c/responses?filter=best

- Instruction

    ```
    python medium.py --help
    python medium.py --name <username> --min-recommendations 1
    ```
