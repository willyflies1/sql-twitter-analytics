from flask import Flask, render_template, session, redirect, request, url_for, g
import requests
from src.database import Database
from src.twitter_utils import get_request_token, get_oauth_verifier_url, get_access_token
from src.user import User

app = Flask(__name__)
app.secret_key = 'JohnSnow'

Database.initialise(database="learning", host="localhost", user="postgres", password="NightKingSusano7")


# Loads before every request
@app.before_request
def load_user():
    if 'screen_name' in session:
        g.user = User.load_db_by_screen_name(session['screen_name'])


@app.route('/')
def homepage():
    return render_template('home.html')


@app.route('/login/twitter')
def twitter_login():
    # Check to see if they are already logged in, and redirect to their profile
    if 'screen_name' in session:
        return redirect(url_for('profile'))

    # We need a request token 1st...
    request_token = get_request_token()
    session['request_token'] = request_token        # stores the request_token as a cookie

    # Redirect the user to Twitter so they can confirm authorization
    return redirect(get_oauth_verifier_url(request_token))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('homepage'))


@app.route('/auth/twitter')     # http://127.0.0.1:4995/auth/twitter?oauth_verifier=123456789
def twitter_auth():
    oauth_verifier = request.args.get('oauth_verifier')
    # access_token cannot be used more than once
    access_token = get_access_token(session['request_token'], oauth_verifier)

    user = User.load_db_by_screen_name(access_token['screen_name'])
    if not user:
        user = User(access_token['screen_name'], access_token['oauth_token'],
                    access_token['oauth_token_secret'], id=None)
        user.save_to_db()

    session['screen_name'] = user.screen_name

    return redirect(url_for('profile'))


@app.route('/profile')
def profile():
    return render_template('profile.html', user=g.user)


@app.route('/search')       # http://127.0.0.1:4995/search?q=cars+filter:images
def search():
    query = request.args.get('q')

    # computers+filter:images
    tweets = g.user.user_request('https://api.twitter.com/1.1/search/tweets.json?q={}'.format(query))

    tweet_texts = [{'tweet': tweet['text'], 'label': 'neutral'} for tweet in tweets['statuses']]

    for tweet in tweet_texts:
        r = requests.post('http://text-processing.com/api/sentiment/', data={'text': tweet['tweet']})
        json_response = r.json()
        label = json_response['label']
        tweet['label'] = label
    return render_template('search.html', content=tweet_texts)


app.run(port=4995, debug=True)
