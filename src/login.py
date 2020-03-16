from src.database import Database
from src.user import User
import src.constants as constants
import oauth2
from src.twitter_utils import consumer, get_request_token, get_oauth_verifier, \
    get_access_token

# Initialise database
Database.initialise(database="learning", host="localhost", user="postgres", password="NightKingSusano7")

user_email = input("Enter your email address: ")
user = User.load_db_by_email(user_email)

if user:
    print("Signed in under email: {} ".format(user_email))
else:

    print("There is no login with email={} \n".format(user_email))

    request_token = get_request_token()

    oauth_verifier = get_oauth_verifier(request_token)

    access_token = get_access_token(request_token, oauth_verifier)

    first_name = input("Enter your first name: ")
    last_name = input("Enter your last name: ")

    user = User(user_email, first_name, last_name,access_token['oauth_token'],
                oauth_token_secret=access_token['oauth_token_secret'], id=None)
    user.save_to_db()

tweets = user.twitter_requests('https://api.twitter.com/1.1/search/tweets.json?q=computers+filter:images')

for tweet in tweets['statuses']:
    print(tweet['text'])

