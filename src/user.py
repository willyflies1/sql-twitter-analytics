# Stores the class that we are modeling the users with
import json
import oauth2
from src.twitter_utils import consumer
from src.database import CursorFromConnectionFromPool


class User:

    # (self, email, first_name, last_name, oauth_token, oauth_token_secret, id)
    def __init__(self, screen_name, oauth_token, oauth_token_secret, id):
        #self.email = email
        #self.first_name = first_name
        #self.last_name = last_name
        self.screen_name = screen_name
        self.oauth_token = oauth_token
        self.oauth_token_secret = oauth_token_secret
        self.id = id

    # print(User) => ...
    def __repr__(self):
        return "<User {}>".format(self.screen_name)

    # Save the user to DB
    def save_to_db(self):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute('INSERT INTO users (screen_name, oauth_token, oauth_token_secret) '
                           'VALUES (%s, %s, %s)',
                           (self.screen_name, self.oauth_token, self.oauth_token_secret))

    @classmethod    # does not bound the currently bound object, but the class object
    def load_db_by_screen_name(cls, screen_name):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute('SELECT * FROM users WHERE screen_name=%s', (screen_name,))  # '(email,) tells python its a tuple
            user_data = cursor.fetchone()
            if user_data: # user_data
                return cls(screen_name=user_data[1],
                           oauth_token=user_data[2],
                           oauth_token_secret=user_data[3],
                           id=user_data[0])

    def  user_request(self, uri, verb='GET'):
        # Create an 'authenticated_token' Token object and use that to perform Twitter API calls on
        # behalf of the user
        # authorized_token = oauth2.Token(key=access_token['oauth_token'], secret=access_token['oauth_token_secret'])
        authorized_token = oauth2.Token(key=self.oauth_token, secret=self.oauth_token_secret)
        authorized_client = oauth2.Client(consumer, authorized_token)

        # Make Twitter API calls!
        response, content = authorized_client.request(uri, verb)
        if response.status != 200:
            print("An error occurred when search was done")

        return json.loads(content.decode('utf-8'))
