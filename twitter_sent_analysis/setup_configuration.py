#
# Generates a twitter_configuration.ini file with Twitter Developers API Keys
from pathlib import Path


def get_mysql_configuration():
    mysql_conf_dict = {}

    mysql_conf_dict['HOST'] = input(
        "Hostname (i.e. localhost): ")
    mysql_conf_dict['USERNAME'] = input(
        "MySQL Username: ")
    mysql_conf_dict['PASSWORD'] = input(
        "MySQL User Password: ")
    mysql_conf_dict['DATABASE'] = input(
        "MySQL Database Name(i.e. twitter_db): ")
    mysql_conf_dict['TABLE'] = input(
        "MySQL Table Name(i.e. TWEETS_BY_KEYWORD): ")

    return mysql_conf_dict


def get_twitter_configuration():
    twitter_conf_dict = {}

    twitter_conf_dict['CONSUMER_KEY'] = input(
        "Twitter CONSUMER_KEY: ")
    twitter_conf_dict['CONSUMER_SECRET'] = input(
        "Twitter CONSUMER_SECRET: ")
    twitter_conf_dict['ACCESS_TOKEN'] = input(
        "Twitter ACCESS_TOKEN: ")
    twitter_conf_dict['ACCESS_TOKEN_SECRET'] = input(
        "Twitter ACCESS_TOKEN_SECRET: ")

    return twitter_conf_dict


def write_to_conf_file():
    mysql_conf_dict = get_mysql_configuration()
    twitter_conf_dict = get_twitter_configuration()

    with open('twitter_configuration_secret.ini', 'w') as fptr:
        fptr.write("[MYSQL]\n")

        fptr.write(f"HOST: {mysql_conf_dict['HOST']}\n")
        fptr.write(f"USERNAME: {mysql_conf_dict['USERNAME']}\n")
        fptr.write(f"PASSWORD: {mysql_conf_dict['PASSWORD']}\n")
        fptr.write(f"TABLE: {mysql_conf_dict['TABLE']}\n")
        fptr.write(f"DATABASE: {mysql_conf_dict['DATABASE']}\n")
        fptr.write('\n')

        fptr.write("[TWITTER]\n")

        fptr.write(
            f"CONSUMER_KEY: {twitter_conf_dict['CONSUMER_KEY']}\n")
        fptr.write(
            f"CONSUMER_SECRET: {twitter_conf_dict['CONSUMER_SECRET']}\n")
        fptr.write(
            f"ACCESS_TOKEN: {twitter_conf_dict['ACCESS_TOKEN']}\n")
        fptr.write(
            f"ACCESS_TOKEN_SECRET: {twitter_conf_dict['ACCESS_TOKEN_SECRET']}\n")


def gen_conf_file():
    conf_file = Path('./twitter_configuration_secret.ini')

    write = input("twitter_configuration_secret.ini already exists. "
                  + "Do you want to override? (y/n):") \
        if conf_file.is_file() else 'Y'

    if write in ('Y', 'y', 'YES', 'yes', 'Yes'):
        write_to_conf_file()
    else:
        print("No configuration file generated")


if __name__ == "__main__":
    gen_conf_file()
