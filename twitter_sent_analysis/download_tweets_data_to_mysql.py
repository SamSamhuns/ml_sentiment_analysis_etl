import sys
import json
import tweepy
import argparse
import mysql.connector
from dateutil import parser
from mysql.connector import Error
from twitter_config_loader import TwitterConfig
from twitter_config_loader import print_error
from twitter_config_loader import print_warning

DEBUG = True


class TweepyConfig:
    ''' Class for creating tweepy API objects loaded with twitter API keys '''

    def __init__(self, cur_config):
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

    def __init__(self):
        super().__init__()
        self.tweet_download_limit = 10000
        self.tweet_download_count = 0

    def on_connect(self):
        print("Connected to the Twitter API now")

    def on_status(self, status):
        if not(status.retweeted_status):
            if DEBUG:
                print(self.status)

    def on_data(self, data):
        ''' Read tweets as JSON objs and extract data '''
        json_data = json.loads(data)

        tweet_id = json_data['id']
        tweet = json_data['text']
        created_at = parser.parse(json_data['created_at'])
        reply_count = json_data['reply_count']
        retweet_count = json_data['retweet_count']
        user_name = json_data['user']['screen_name']
        user_friends_count = json_data['user']['friends_count']
        user_followers_count = json_data['user']['followers_count']
        tweet_place = json_data['place']['country'] if \
            json_data['place'] != None else 'NULL'

        try:
            favorite_count = json_data['favorite_count']
        except Exception as e:
            if DEBUG:
                print_warning()
            favorite_count = 0
        try:
            user_location = json_data['user']['location']
        except Exception as e:
            if DEBUG:
                print_warning()
            user_location = "NULL"

        self.tweet_download_count += 1
        if self.tweet_download_count > self.tweet_download_limit:
            print(
                "Personal Tweet access limit reached. Aborting now. [This can be altered]")
            return False

        insert_tweets_in_mysql_db(tweet_id, tweet, created_at, tweet_place, favorite_count,
                                  retweet_count, reply_count, user_name, user_location,
                                  user_followers_count, user_friends_count)

    def on_error(self, status_code):
        # returning False in on_error disconnects the stream
        if status_code == 420:
            print("Request rate limit reached")
            return False

        if status_code != 200:
            print("Error in connecting to twitter API")
            return False

        # returning non-False reconnects the stream, with backoff.


def insert_tweets_in_mysql_db(tweet_id, tweet, created_at, tweet_place, favorite_count,
                              retweet_count, reply_count, user_name, user_location,
                              user_followers_count, user_friends_count):
    ''' Function to connect to the mysql db and insert tweet data '''
    cur_config = TwitterConfig()
    try:
        mysql_con = mysql.connector.connect(
            host=cur_config.MYSQL_HOST,
            user=cur_config.MYSQL_USERNAME,
            password=cur_config.MYSQL_PASSWORD,
            database=cur_config.MYSQL_DATABASE,
            auth_plugin='mysql_native_password',
            charset='utf8mb4')

        if mysql_con.is_connected():
            ''' Insert data from twitter api '''
            cursor = mysql_con.cursor()
            query = f"INSERT INTO {cur_config.MYSQL_TABLE}" +\
                " (tweet_id, tweet, created_at, tweet_place, favorite_count," +\
                " retweet_count, reply_count, user_name, user_location," +\
                " user_followers_count, user_friends_count)" +\
                " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
            cursor.execute(query, (tweet_id, tweet, created_at, tweet_place, favorite_count,
                                   retweet_count, reply_count, user_name, user_location,
                                   user_followers_count, user_friends_count))
            mysql_con.commit()

    except Error as e:
        print_error()
        print(e)

    try:
        cursor.close()
        mysql_con.close()
    except UnboundLocalError:
        print_error()
        sys.exit(-1)

    print(f"Inserted Tweet '{tweet[:(min(len(tweet), 60))]}...'" +
          f"into {cur_config.MYSQL_TABLE}")
    return


def download_tweets_by_keyword(api, tracking_filters):

    customStreamListener = TweetStreamListener()
    customStream = tweepy.Stream(
        auth=api.auth, listener=customStreamListener)

    customStream.filter(track=tracking_filters, languages=['en'])


def download_tweets_by_user_id(api, tracking_filters):

    customStreamListener = TweetStreamListener()
    customStream = tweepy.Stream(
        auth=api.auth, listener=customStreamListener)

    # To specify a particular twitter account i.e.25073877=realDonaldTrump
    customStream.filter(follow=tracking_filters, languages=['en'])


def validate_and_return_args():
    parser = argparse.ArgumentParser(
        description="Download and save tweets to MySQL db based on keywords/user")

    parser.add_argument("download_type",
                        type=str,
                        action='store',
                        default="keyword",
                        choices=['keyword', 'userid'],
                        help="Type of download (default: 'keyword', options: ['keyword', 'userid']) ")
    parser.add_argument("filename",
                        type=str,
                        action='store',
                        help="Name of file containing keywords/userids")

    return parser.parse_args()


def validate_file_and_return_tracking_filter_list(argparse_obj):
    """ Function to validate file exists and generate a list of keywords or userids"""
    with open(argparse_obj.filename, "r") as file:
        kw_list = file.read()
        kw_list = kw_list.strip().split()
        if kw_list != []:
            return kw_list
    raise EOFError


def main():
    cur_config = TwitterConfig()
    api = TweepyConfig(cur_config).tweepy_api()

    argparse_obj = validate_and_return_args()
    tracking_filters = validate_file_and_return_tracking_filter_list(argparse_obj)
    print(
        f"Tracking filter mode set to {argparse_obj.download_type} and filters are {tracking_filters}")

    # Choose the appropriate download mode based on user arguments
    if argparse_obj.download_type == 'keyword':
        download_tweets_by_keyword(api, tracking_filters)
    elif argparse_obj.download_type == 'userid':
        download_tweets_by_user_id(api, tracking_filters)


if __name__ == "__main__":
    main()
