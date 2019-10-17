"""
Utility file containing TwitterConfig configuration data loading class
"""
import sys
import configparser


def print_error_info():
    print(f"Error Type {sys.exc_info()[0]}, description {sys.exc_info()[1]}," +
          f"line: {sys.exc_info()[2].tb_lineno}")


class TwitterConfig:
    ''' Class that loads twitter CONSUMER_KEY and ACCESS_TOKEN from
    configuration.ini '''

    config = configparser.ConfigParser()
    config.read('./twitter_configuration_secret.ini')

    # table where all tweet info is stored
    MYSQL_HOST = config['MYSQL']['HOST']
    MYSQL_TABLE = config['MYSQL']['TABLE']
    MYSQL_DATABASE = config['MYSQL']['DATABASE']
    MYSQL_USERNAME = config['MYSQL']['USERNAME']  # username is set to be root
    MYSQL_PASSWORD = config['MYSQL']['PASSWORD']

    CONSUMER_KEY = config['TWITTER']['CONSUMER_KEY']
    CONSUMER_SECRET = config['TWITTER']['CONSUMER_SECRET']
    ACCESS_TOKEN = config['TWITTER']['ACCESS_TOKEN']
    ACCESS_TOKEN_SECRET = config['TWITTER']['ACCESS_TOKEN_SECRET']
