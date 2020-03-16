import oauth2
from src import constants
import urllib.parse as urlparse

# Create a consumer, which uses CONSUMER_KEY AND CONSUMER_SECRET to identify our app uniquely
consumer = oauth2.Consumer(constants.CONSUMER_KEY, constants.CONSUMER_SECRET)


def get_request_token():
    client = oauth2.Client(consumer)

    # Use the client to perform a request for the request token
    response, content = client.request(constants.REQUEST_TOKEN_URL, 'POST')
    if response.status != 200:
        print("An error occurred getting the request token from Twitter!")

        # Get the request token parsing the query string returned
    return dict(urlparse.parse_qsl(content.decode('utf-8')))


def get_oauth_verifier(request_token):
    print("Go to the following site in your browser:")
    print(get_oauth_verifier_url(request_token))

    # In console applications, the user has to enter this pin themselves
    # In web applications, twitter would send it themselves
    return input("What is the PIN? ")


def get_oauth_verifier_url(request_token):
    return "{}?oauth_token={}".format(constants.AUTHORIZATION_URL, request_token['oauth_token'])


def get_access_token(request_token, oauth_verifier):
    # Create a Token object which contains the request token, and the verifier
    token = oauth2.Token(key=request_token['oauth_token'], secret=request_token['oauth_token_secret'])
    token.set_verifier(verifier=oauth_verifier)

    # Create a client with our consumer (our app) and the newly created (and verified) token
    client = oauth2.Client(consumer, token=token)

    # Ask twitter for an access token, and twitter knows it should give us it because
    # we've verified the request token
    response, content = client.request(constants.ACCESS_TOKEN_URL, 'POST')
    return dict(urlparse.parse_qsl(content.decode('utf-8')))