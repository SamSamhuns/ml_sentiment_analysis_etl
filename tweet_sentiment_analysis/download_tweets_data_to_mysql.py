import sys
import json
import tweepy
import configparser
import mysql.connector
from dateutil import parser
from mysql.connector import Error

DEBUG = True


def print_error_info():
    print(f"Error Type {sys.exc_info()[0]}, description {sys.exc_info()[1]}," +
          f"line: {sys.exc_info()[2].tb_lineno}")


class TwitterConfig:
    ''' Class that loads twitter CONSUMER_KEY and ACCESS_TOKEN from
    configuration.ini '''

    config = configparser.ConfigParser()
    config.read('./configuration.ini')

    # table where all tweet info is stored
    MYSQL_TABLE = config['MYSQL']['TABLE']
    MYSQL_DATABASE = config['MYSQL']['DATABASE']
    MYSQL_PASSWORD = config['MYSQL']['PASSWORD']  # username is set to be root

    CONSUMER_KEY = config['TWITTER']['CONSUMER_KEY']
    CONSUMER_SECRET = config['TWITTER']['CONSUMER_SECRET']
    ACCESS_TOKEN = config['TWITTER']['ACCESS_TOKEN']
    ACCESS_TOKEN_SECRET = config['TWITTER']['ACCESS_TOKEN_SECRET']


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
        self.limit = 30  # number of tweets to download in one session
        self.counter = 0  # counter to count tweets

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
        retweet_count = json_data['retweet_count']
        reply_count = json_data['reply_count']
        user_name = json_data['user']['screen_name']
        user_followers_count = json_data['user']['followers_count']
        user_friends_count = json_data['user']['friends_count']
        # tweet_place = "NULL"
        # favorite_count = "NULL"
        # user_location = "NULL"

        try:
            tweet_place = json_data['place']['country']
        except Exception as e:
            if DEBUG:
                print_error_info()
            tweet_place = "NULL"
        try:
            favorite_count = json_data['favorite_count']
        except Exception as e:
            if DEBUG:
                print_error_info()
            favorite_count = 0
        try:
            user_location = json_data['user']['location']
        except Exception as e:
            if DEBUG:
                print_error_info()
            user_location = "NULL"

        self.counter += 1
        if self.counter > self.limit:
            print(
                "Personal Tweet access limit reached. Aborting now. [This can be altered]")
            return False

        # Call insert_tweets_in_mysql_db()
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
        mysql_cnx = mysql.connector.connect(
            host='localhost',
            user='root',
            password=cur_config.MYSQL_PASSWORD,
            database=cur_config.MYSQL_DATABASE,
            auth_plugin='mysql_native_password',
            charset='utf8')

        if mysql_cnx.is_connected():
            ''' Insert data from twitter api '''
            cursor = mysql_cnx.cursor()
            query = f"INSERT INTO {cur_config.MYSQL_TABLE}" +\
                " (tweet_id, tweet, created_at, tweet_place, favorite_count," +\
                " retweet_count, reply_count, user_name, user_location," +\
                " user_followers_count, user_friends_count)" +\
                " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
            cursor.execute(query, (tweet_id, tweet, created_at, tweet_place, favorite_count,
                                   retweet_count, reply_count, user_name, user_location,
                                   user_followers_count, user_friends_count))
            mysql_cnx.commit()

    except Error as e:
        print(e)

    cursor.close()
    mysql_cnx.close()
    return


def download_tweet_data(api, tracking_filters):

    customStreamListener = TweetStreamListener()
    customStream = tweepy.Stream(
        auth=api.auth, listener=customStreamListener)

    customStream.filter(track=tracking_filters, languages=['en'])

    # To specify a particular twitter account i.e.25073877=realDonaldTrump
    # myStream.filter(follow=["25073877"])


def main():
    cur_config = TwitterConfig()
    api = TweepyConfig(cur_config).tweepy_api()
    tracking_filters = ['batman', 'joker']
    download_tweet_data(api, tracking_filters)


if __name__ == "__main__":
    main()
