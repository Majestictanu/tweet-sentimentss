from flask import Flask, render_template, request
import tweepy
import re
import time
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from tweepy.errors import TooManyRequests

app = Flask(_name_)

# Twitter API credentials
API_KEY = "efeQNSFfwB2Qx3M8sYSQK5kd4S"
API_SECRET = "KSVMlQok14s3OWQkIa4UHDGvFiSr7ptzvD01ieJuyiEcwDtRXS"
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAMkn0QEAAAAAyZLBjv996qeeaf%2BcZaR4xaARfrw%3D3KzMuZkAPOyz1Dvn8HEOYh7KTwd1joTExv6lOD4OnEAlau8Y8T"

# Authenticate
client = tweepy.Client(bearer_token=BEARER_TOKEN)

# Function to clean tweets
def clean_tweet(text):
    text = re.sub(r"http\S+", "", text)  # Remove URLs
    text = re.sub(r"@\S+", "", text)  # Remove mentions
    text = re.sub(r"#\S+", "", text)  # Remove hashtags
    text = re.sub(r"[^A-Za-z0-9 ]+", "", text)  # Remove special characters
    text = text.replace("Bitcon", "Bitcoin")  # Fix the typo "Bitcon" to "Bitcoin"
    return text.lower().strip()

# Function to analyze sentiment
def analyze_sentiment(text):
    analyzer = SentimentIntensityAnalyzer()
    sentiment_score = analyzer.polarity_scores(text)
    if sentiment_score['compound'] >= 0.1:  # Adjusted threshold for positive
        return 'Positive'
    elif sentiment_score['compound'] <= -0.1:  # Adjusted threshold for negative
        return 'Negative'
    else:
        return 'Neutral'

# Function to fetch tweets with rate limit handling
def fetch_tweets(query):
    try:
        tweets = client.search_recent_tweets(query=query, max_results=10)
        return tweets
    except TooManyRequests as e:
        # If rate limit is exceeded, get the reset time from the header
        reset_time = e.response.headers.get('x-rate-limit-reset')
        
        if reset_time:
            reset_time = int(reset_time)
            sleep_time = reset_time - int(time.time()) + 5  # Wait 5 seconds after the reset time
            print(f"Rate limit hit. Sleeping for {sleep_time} seconds.")
            time.sleep(sleep_time)  # Sleep until rate limit is reset
            return fetch_tweets(query)  # Retry after sleep
        else:
            print("Too many requests, retrying in 60 seconds...")
            time.sleep(60)  # Default wait if no reset time is given
            return fetch_tweets(query)  # Retry the request after sleep

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        query = request.form["query"]
        # Fetch tweets on user input
        tweets = fetch_tweets(query)  # Use the updated fetch_tweets function
        
        results = []
        if tweets.data:
            for tweet in tweets.data:
                cleaned_text = clean_tweet(tweet.text)
                sentiment = analyze_sentiment(cleaned_text)
                results.append({"tweet": tweet.text, "sentiment": sentiment})

        return render_template("index.html", results=results, query=query)
    return render_template("index.html", results=None)

if _name_ == "_main_":
    app.run(debug=True)