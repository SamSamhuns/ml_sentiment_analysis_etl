import os
import sys
import gzip
import json
import tweepy
import argparse

from time import time
from typing import List
from dateutil import parser
from twitter_config_loader import TwitterConfig
from twitter_config_loader import print_error
from twitter_config_loader import print_warning

DEBUG = True


class TweepyConfig:
    ''' Class for creating tweepy API objects loaded with twitter API keys '''

    def __init__(self, cur_config: 'TwitterConfig') -> None:
        self.auth = tweepy.OAuthHandler(
            cur_config.CONSUMER_KEY,
            cur_config.CONSUMER_SECRET)
        self.auth.set_access_token(
            cur_config.ACCESS_TOKEN,
            cur_config.ACCESS_TOKEN_SECRET)

    def tweepy_api(self):
        return tweepy.API(self.auth, wait_on_rate_limit=True)


class TweetStreamListener(tweepy.StreamListener):
    ''' Tweepy listener class that inherits from tweepy.StreamListener '''

    def __init__(self) -> None:
        super().__init__()
        self.tweet_download_limit = 10000000
        self.tweet_download_count = 0

    def on_connect(self) -> None:
        print("Connected to the Twitter API now")

    def on_status(self, status):
        if not(status.retweeted_status):
            if DEBUG:
                print(self.status)

    def on_data(self, data):
        ''' Read tweets as JSON objs and extract data '''
        json_data = json.loads(data)

        with gzip.open(f'json/{str(time())[:7]}.jsonl.gz', 'a') as output:
            output.write(json.dumps(json_data).encode('utf8') + b"\n")

        self.tweet_download_count += 1
        if self.tweet_download_count > self.tweet_download_limit:
            print(
                "Personal Tweet access limit reached. Aborting now. [This can be altered]")
            return False

    def on_error(self, status_code):
        # returning False in on_error disconnects the stream
        if status_code == 420:
            print("Request rate limit reached")
            return False

        if status_code != 200:
            print("Error in connecting to twitter API")
            return False

        # returning non-False reconnects the stream, with backoff.


def download_tweets_by_filters(api,
                               track: List[str] = [],
                               follow: List[str] = [],
                               locations: List[str] = [],
                               languages: List[str] = ['en']):

    customStreamListener = TweetStreamListener()
    customStream = tweepy.Stream(
        auth=api.auth, listener=customStreamListener)

    # To specify a particular twitter account i.e.25073877=realDonaldTrump
    customStream.filter(track=track,
                        follow=follow,
                        locations=locations,
                        languages=languages)


def validate_and_return_args():
    parser = argparse.ArgumentParser(
        description="Download and save tweets to MySQL " +
                    "db based on keywords, userid or geolocation")

    parser.add_argument('-t',
                        '--track',
                        type=str,
                        nargs='?',
                        action='store',
                        default=None,
                        help="Name of file containing keywords i.e. batman,joker")
    parser.add_argument('-f',
                        '--follow',
                        type=str,
                        nargs='?',
                        action='store',
                        default=None,
                        help="Name of file containing userids i.e. 25073877")
    parser.add_argument('-l',
                        '--locations',
                        type=str,
                        nargs='?',
                        action='store',
                        default=None,
                        help="Name of file containing geo-locations i.e. -122.75,36.8,-121.75,37.8,-74,40,-73,41")

    return parser.parse_args()


def validate_file_and_rtn_filter_list(filename):
    """ Function to validate file exists and generate a list of keywords or userids"""
    if filename is None:
        return []
    with open(filename, "r") as file:
        kw_list = file.read()
        kw_list = kw_list.strip().split()
        if kw_list != []:
            return kw_list
    raise EOFError


def main():
    cur_config = TwitterConfig()
    api = TweepyConfig(cur_config).tweepy_api()

    argparse_obj = validate_and_return_args()

    if (argparse_obj.track is None
        and argparse_obj.follow is None
            and argparse_obj.locations is None):
        print("No filters files selected. Please add them")
        return -1

    track_filter = validate_file_and_rtn_filter_list(
        argparse_obj.track)
    follow_filter = validate_file_and_rtn_filter_list(
        argparse_obj.follow)
    location_filter = validate_file_and_rtn_filter_list(
        argparse_obj.locations)

    print("Active tracking filters are:")
    if argparse_obj.track:
        print(f"\tKeywords from {argparse_obj.track}")
    if argparse_obj.follow:
        print(f"\tUserids from {argparse_obj.follow}")
    if argparse_obj.locations:
        print(f"\tLocations from {argparse_obj.locations}")

    os.makedirs("json", exist_ok=True)
    download_tweets_by_filters(api,
                               track=track_filter,
                               follow=follow_filter,
                               locations=location_filter)


if __name__ == "__main__":
    main()
