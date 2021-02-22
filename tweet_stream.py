
import csv
import json
import os
import sys

import click
from tweepy import OAuthHandler, Stream, API
from tweepy.streaming import StreamListener

from settings.twitter_settings import KEY, SECRET, TOKEN, TOKEN_SECRET
from settings.aws_settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

auth = OAuthHandler(KEY, SECRET)
auth.set_access_token(TOKEN, TOKEN_SECRET)
api = API(auth)
counter = 0

class TweetsListener(StreamListener):
    """
        Extends tweepy.StreamListener
        Custom tweet logging and extracting.
        Saves tweets extracted in an output csv file
    """
    def __init__(self, tweet_limit):
        """
            Redefining Constructor: adding a limit of tweets to stream.
        """
        super().__init__()
        self.tweet_limit = tweet_limit

    def on_status(self, status):
        """
            Redefining on_stats methos for custom tweets processing.
        """
        print(status.id_str)
        is_retweet = hasattr(status, "retweeted_status")

        if hasattr(status, "extended_tweet"):
            text = status.extended_tweet["full_text"]
        else:
            text = status.text

        is_quote = hasattr(status, "quoted_status")
        quoted_text = ""

        if is_quote:
            if hasattr(status.quoted_status, "extended_tweet"):
                quoted_text = status.quoted_status.extended_tweet["full_text"]
            else:
                quoted_text = status.quoted_status.text

        remove_characters = [",","\n", "\'", "RT", "`s"]
        for c in remove_characters:
            text = text.replace(c," ")
            quoted_text = quoted_text.replace(c, " ")

        os.makedirs("data", exist_ok=True)

        with open(f"data/out.csv", "a", encoding='utf-8') as out:
            global counter
            counter += 1
            csv_out = csv.writer(out)
            data = (str(status.created_at.date()),
                    text, status.user.location, is_retweet, 
                    is_quote, status.place)
            print(data)
            csv_out.writerow(data)
            
            if counter == self.tweet_limit:
                print("\n\n###########################")
                print("## Tweets Limit Reached! ##")
                print(f"### {counter} tweets extracted ###")
                print("###########################\n\n")
                sys.exit()

    def on_error(self, status_code):
        """
            Redefining on_error method for when tweets processung fails
        """
        print(f"Encountered streaming error {status_code}")
        return True

@click.command()
@click.option('--tweet_limit', prompt='Enter the number of tweets that you want to stream',
              help='Must be an integer')
@click.option('--topic', prompt='Enter the topic to track in twitter',
              help='Must be an string with a real topic')

def main(topic, tweet_limit):

    tweet_listener = TweetsListener(int(tweet_limit))
    twitter_stream = Stream(auth, tweet_listener, tweet_mode="extended_tweet")
    twitter_stream.filter(track=[topic], languages=["en"])

if __name__ == "__main__":
    main()
