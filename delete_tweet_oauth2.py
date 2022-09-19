import time
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import TokenExpiredError
import os
import json
from dotenv import load_dotenv

class OldTweetsEraser:
    client_id = ''
    redirect_uri = ''
    scope = ''
    client_secret = ''
    username = ''

    oauth = None

    def load_configuration(self):
        load_dotenv()
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.redirect_uri = os.getenv("REDIRECT_URI")
        self.username = os.getenv("TWITTER_USERNAME")
        self.scope = ['users.read','offline.access','tweet.read','tweet.write']

    def save_token(self, token):
        with open('session.json', 'w') as file:
            json.dump(token, file)

    def load_token(self):
        try:
            with open('session.json','r') as file:
                token = json.load(file)
            return token
        except:
            return None

    def get_new_token(self):
        oauth = OAuth2Session(client_id=self.client_id, redirect_uri=self.redirect_uri, scope=self.scope)
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
            client_secret=self.client_secret,
            code_verifier='challenge'
        )
        self.save_token(token)

    def get_user_id(self):
        print('Getting user id...')
        user_response = self.oauth.get('https://api.twitter.com/2/users/by/username/{}'.format(self.username))
        if user_response.status_code != 200:
            raise Exception(
                "Request returned an error: {} {}".format(user_response.status_code, user_response.text)
            )
        user_json = user_response.json()
        user_fullname = user_json['data']['name']

        self.user_id = user_json['data']['id']
        print('got user id: {}, name: {} from twitter username: {}'.format(self.user_id, user_fullname, self.username))

    def main(self):
        # load configuration from .env file
        self.load_configuration()

        if self.username is None:
            raise Exception(
                "Twitter Username cannot be blank, Set it in your .env file TWITTER_USERNAME=your_current_twitter_username"
            )

        token = self.load_token()
        if token is None:
            self.get_new_token()
        else:
            self.oauth = OAuth2Session(client_id=self.client_id, token=token)

        try:
            self.get_user_id()
        except TokenExpiredError:
            self.get_new_token()
            self.get_user_id()

        if self.user_id == 0:
            raise Exception(
                "User Id Not Valid"
            )

        # Making the request
        count = 0
        while True:
            try:
                tweets_response = self.oauth.get("https://api.twitter.com/2/users/{}/tweets".format(self.user_id))
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

                    delete_response = self.oauth.delete("https://api.twitter.com/2/tweets/{}".format(id))
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
                token = self.oauth.refresh_token(
                    'https://api.twitter.com/2/oauth2/token',
                    refresh_token=token['refresh_token'],
                    client_id=self.client_id
                )
                self.save_token(token)

if __name__ == '__main__':
    service = OldTweetsEraser()
    service.main()