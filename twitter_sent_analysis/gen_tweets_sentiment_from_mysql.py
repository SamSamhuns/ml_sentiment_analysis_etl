import re
import os
import numpy as np
import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt
from mysql.connector import Error

from textblob import TextBlob
from wordcloud import WordCloud, STOPWORDS
from twitter_config_loader import TwitterConfig
from twitter_config_loader import print_error
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

import nltk
nltk.download('stopwords')
nltk.download('wordnet')


class TweetObject:

    def __init__(self, host, user, password, database):
        self.MYSQL_HOST = host
        self.MYSQL_USER = user
        self.MYSQL_PASSWORD = password
        self.MYSQL_DATABASE = database

    def connect_mysql_and_get_dataframe(self, query):
        """ Retrieve data from sql db
            and return as a Pandas dataframe """
        try:
            mysql_con = mysql.connector.connect(
                host=self.MYSQL_HOST,
                user=self.MYSQL_USER,
                password=self.MYSQL_PASSWORD,
                database=self.MYSQL_DATABASE,
                auth_plugin='mysql_native_password',
                charset='utf8mb4'
            )

            if mysql_con.is_connected():
                print(
                    f"Connected to {self.MYSQL_DATABASE} as {self.MYSQL_USER} now")
                cursor = mysql_con.cursor()
                cursor.execute(query)

                fetched_data = cursor.fetchall()
                # load fetched_data in dataframe
                tweet_df = pd.DataFrame(fetched_data, columns=[
                                        'created_at', 'tweet'])

        except Error as e:
            print(e)
        cursor.close()
        mysql_con.close()
        return tweet_df

    def preprocess_tweets(self, tweet_df):
        """ Take orginial tweets as a Pandas df and normalize them
            by removing punctuation, stop words, hmtl, emoticons and
            convert uppercase to lowercase. Gen canonical form using
            WordNetLemmatizer """
        stopwords_list = stopwords.words('english')
        wordnet_lemmatizer = WordNetLemmatizer()
        tweet_df['clean_tweets'] = None
        tweet_df['tweet_len'] = None
        tweet_text_col_name = "tweet"

        for i in range(len(tweet_df[tweet_text_col_name])):
            ''' iterate through all the tweets and remove all non-letter chars '''
            exclude_items = ['[^a-zA-Z]', 'rt', 'http', 'RT', 'co']
            exclude = '|'.join(exclude_items)

            # re.sub(pattern, repl, string)
            tweet_text = re.sub(exclude, ' ', tweet_df[tweet_text_col_name][i])
            tweet_text = tweet_text.lower()
            tweet_words = tweet_text.split()
            tweet_words = [wordnet_lemmatizer.lemmatize(
                word) for word in tweet_words if not word in stopwords_list and len(word) > 1]

            tweet_df['clean_tweets'][i] = ' '.join(tweet_words)

        # Save length of each tweet object in column "tweet_len"
        tweet_df['tweet_len'] = np.array(
            [len(word) for word in tweet_df['clean_tweets']])

        return tweet_df

    def generate_sentiment(self, tweet_text):
        ''' Function takes in the tweet text
            and returns a sentiment polarity score
            -1, 0, or 1'''

        tweet_analysis = TextBlob(tweet_text)
        if tweet_analysis.sentiment.polarity > 0:
            return 1   # Postive
        elif tweet_analysis.sentiment.polarity == 0:
            return 0   # Neutral
        else:
            return -1  # Negative

    def save_df_as_csv(self, tweet_df, csv_name="cleaned_tweets.csv"):
        try:
            os.makedirs("csv", exist_ok=True)
            tweet_df.to_csv(f'./csv/{csv_name}')
            print(f"{csv_name} saved successfully in ./csv/{csv_name}")

        except Error as e:
            print(e)
            print_error()

    def gen_word_cloud(self, tweet_df, wordcloud_img_name="clean_tweets_word_cloud.jpg"):
        """ Take in a tweet_df and plot a WordCloud with matplotlib """
        plt.figure(figsize=(5, 6))
        tweet_wordcloud = WordCloud(
            background_color="white",
            height=1000,
            width=800).generate(
            " ".join(tweet_df['clean_tweets']))

        plt.imshow(tweet_wordcloud, interpolation='bilinear')
        plt.axis('off')
        os.makedirs("img", exist_ok=True)
        plt.savefig(f'./img/{wordcloud_img_name}')
        plt.show()


def main():
    cur_config = TwitterConfig()
    tweet_obj = TweetObject(cur_config.MYSQL_HOST, cur_config.MYSQL_USERNAME,
                            cur_config.MYSQL_PASSWORD, cur_config.MYSQL_DATABASE)

    tweet_df = tweet_obj.connect_mysql_and_get_dataframe(
        f"SELECT created_at,tweet FROM {cur_config.MYSQL_TABLE};")

    processed_tweets = tweet_obj.preprocess_tweets(tweet_df)
    processed_tweets['sentiment'] = [tweet_obj.generate_sentiment(
        text) for text in processed_tweets['clean_tweets']]

    print(
        "Percentage of Positive tweets {0:.2f}%".format((processed_tweets['sentiment'].value_counts()[1] / processed_tweets.shape[0]) * 100))
    print(
        "Percentage of Neutral tweets {0:.2f}%".format((processed_tweets['sentiment'].value_counts()[0] / processed_tweets.shape[0]) * 100))
    print(
        "Percentage of Negative tweets {0:.2f}%".format((processed_tweets['sentiment'].value_counts()[-1] / processed_tweets.shape[0]) * 100))

    # The names of the jpg and the csv files can be altered
    tweet_obj.gen_word_cloud(processed_tweets, "trump_tweets_word_cloud.jpg")
    tweet_obj.save_df_as_csv(processed_tweets, "trump_tweets.csv")


if __name__ == "__main__":
    main()
