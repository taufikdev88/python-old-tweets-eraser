import time
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import TokenExpiredError
import os
import json
from dotenv import load_dotenv

def save_token(token):
    with open('session.json', 'w') as file:
        json.dump(token, file)

def load_token():
    try:
        with open('session.json','r') as file:
            token = json.load(file)
        return token
    except:
        return None

# In your terminal please set your environment variables by running the following lines of code.
load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")
username = os.getenv("TWITTER_USERNAME")

if username is None:
    raise Exception(
        "Twitter Username cannot be blank, Set it in your .env file TWITTER_USERNAME=your_current_twitter_username"
    )

scope = ['users.read','offline.access','tweet.read','tweet.write']

token = load_token()
if token is None:
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
    save_token(token)
else:
    oauth = OAuth2Session(client_id=client_id, token=token)

user_response = oauth.get('https://api.twitter.com/2/users/by/username/{}'.format(username))
if user_response.status_code != 200:
    raise Exception(
        "Request returned an error: {} {}".format(user_response.status_code, user_response.text)
    )
user_json = user_response.json()
user_id = user_json['data']['id']
user_fullname = user_json['data']['name']
print('got user id: {}, name: {} from twitter username: {}'.format(user_id, user_fullname, username))

# Making the request
count = 0
while True:
    try:
        tweets_response = oauth.get("https://api.twitter.com/2/users/{}/tweets".format(user_id))
        if tweets_response.status_code != 200:
            raise Exception(
                "Request returned an error: {} {}".format(tweets_response.status_code, tweets_response.text)
            )

        tweets_json = tweets_response.json()
        print(tweets_json)
        for tweet in tweets_json["data"]:
            count = count + 1
            id = tweet["id"]
            text = tweet["text"]
            print("{}\tdeleting {} text: {}".format(count, id, text))

            delete_response = oauth.delete("https://api.twitter.com/2/tweets/{}".format(id))
            if delete_response.status_code == 429:
                print('got rate limited from twitter, waiting for 15 minutes...')
                time.sleep(15*61)

            elif delete_response.status_code != 200:
                raise Exception(
                    "Request returned an error: {} {}".format(delete_response.status_code, delete_response.text)
                )

            # Saving the response as JSON
            json_response = delete_response.json()
            print(json_response)
            time.sleep(0.1)
    except TokenExpiredError as e:
        print('refreshing access token')
        token = oauth.refresh_token(
            'https://api.twitter.com/2/oauth2/token',
            refresh_token=token['refresh_token'],
        )
        save_token(token)