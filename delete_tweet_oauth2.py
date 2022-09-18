import time
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import os
import json
from dotenv import load_dotenv

# In your terminal please set your environment variables by running the following lines of code.
load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")
scope = ['users.read','offline.access','tweet.read','tweet.write']

oauth = OAuth2Session(client_id=client_id, redirect_uri=redirect_uri, scope=scope)
authorization_url, state = oauth.authorization_url(
    'https://twitter.com/i/oauth2/authorize',
    code_challenge='challenge',
    code_challenge_method='plain'
    )
print('Please go to %s and authorize access.' % authorization_url)

authorization_response = input('Enter the full callback URL:')
token = oauth.fetch_token(
    'https://api.twitter.com/2/oauth2/token',
    authorization_response=authorization_response,
    client_secret=client_secret,
    code_verifier='challenge'
)

# Making the request
count = 0
while True:
    if count > 50:
        print('refreshing access token')
        time.sleep(1)
        token = oauth.refresh_token(
            'https://api.twitter.com/2/oauth2/token',
            refresh_token=token['refresh_token'],
        )
        count = 0

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
        if delete_response.status_code == 429:
            print('waiting for 15 minutes...')
            time.sleep(15*61)
            
        elif delete_response.status_code != 200:
            raise Exception(
                "Request returned an error: {} {}".format(delete_response.status_code, delete_response.text)
            )

        # Saving the response as JSON
        json_response = delete_response.json()
        print(json_response)
        time.sleep(0.1)