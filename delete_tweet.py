import time
from requests_oauthlib import OAuth1Session
import os
from dotenv import load_dotenv

# In your terminal please set your environment variables by running the following lines of code.
load_dotenv()
consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")

# Get request token
request_token_url = "https://api.twitter.com/oauth/request_token"
oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)

fetch_response = oauth.fetch_request_token(request_token_url)

resource_owner_key = fetch_response.get("oauth_token")
resource_owner_secret = fetch_response.get("oauth_token_secret")
print("Got OAuth token: %s" % resource_owner_key)

# Get authorization
base_authorization_url = "https://api.twitter.com/oauth/authorize"
authorization_url = oauth.authorization_url(base_authorization_url)
print("Please go here and authorize: %s" % authorization_url)
verifier = input("Paste the PIN here: ")

# Get the access token
access_token_url = "https://api.twitter.com/oauth/access_token"
oauth = OAuth1Session(
    consumer_key,
    client_secret=consumer_secret,
    resource_owner_key=resource_owner_key,
    resource_owner_secret=resource_owner_secret,
    verifier=verifier,
)
oauth_tokens = oauth.fetch_access_token(access_token_url)

access_token = oauth_tokens["oauth_token"]
access_token_secret = oauth_tokens["oauth_token_secret"]

# Make the request
oauth = OAuth1Session(
    consumer_key,
    client_secret=consumer_secret,
    resource_owner_key=access_token,
    resource_owner_secret=access_token_secret,
)

# Making the request
count = 0
while True:
  tweets_response = oauth.get("https://api.twitter.com/2/users/1512683503/tweets")
  if tweets_response.status_code != 200:
    raise Exception(
        "Request returned an error: {} {}".format(tweets_response.status_code, tweets_response.text)
    )

  tweets_json = tweets_response.json()
  for tweet in tweets_json["data"]:
    count = count + 1
    id = tweet["id"]
    text = tweet["text"]
    print("{}\tdeleting {} text: {}".format(count, id, text))

    delete_response = oauth.delete("https://api.twitter.com/2/tweets/{}".format(id))
    if delete_response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(delete_response.status_code, delete_response.text)
        )

    # Saving the response as JSON
    json_response = delete_response.json()
    print(json_response)
    time.sleep(0.1)