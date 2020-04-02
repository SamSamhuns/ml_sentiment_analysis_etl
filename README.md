# Extract Transform Load Data Pipelines for sentiment analysis

<p align="center">
  <img src='img/etl_headline.jpg' height='250' />
</p>

-   [Twitter feed ETL sentiment analysis based on keyword search.](#data-pipeline-for-sentiment-analysis-of-twitter-feeds)
-   [IMDB movie description sentiment analysis based on movie genre.](#etl-pipeline-for-analysis-of-imdb-movie-descriptions)

<<<<<<< HEAD
## ETL pipeline for sentiment analysis of Twitter feeds based on keywords, userids or geolocation
=======
## General setup

-   Make sure Python is installed and set up a Python virtualenv. Install all dependencies from `requirements.txt`.

```shell
$ pip install virtualenv
$ virtualenv venv/bin/activate
$ source venv/bin/activate
$ pip install -r requirements.txt
```

## ETL pipeline for sentiment analysis of live Twitter feeds based on keywords, userids or geolocation
>>>>>>> c2f89936361fd0a1afbd06d667476253ad56a9df

Download tweets with twitter api, load in an MySQL db, and analyze tweet sentiments all in an ETL pipeline.

### Requirements

-   Python 3
-   Twitter account and API credentials (Access Token from a Twitter app)
-   MySQL database server

### Setup

-   Make sure Python is installed and set up a Python virtualenv. Install all dependencies from `requirements.txt`.

```shell
$ pip install virtualenv
$ virtualenv venv/bin/activate
$ source venv/bin/activate
$ pip install -r requirements.txt
```

-   Run `setup_configuration.py` to use a command prompt to enter all required configurations and generate a `twitter_configuration.ini` file.

-   Or, manually add the required `CONSUMER_KEY`, `CONSUMER_SECRET`, `ACCESS_TOKEN`, `ACCESS_TOKEN_SECRET`, `MYSQL_DATABASE`, `MYSQL_TABLE`, and `MYSQL_PASSWORD` to the `twitter_sent_analysis/twitter_configuration.ini` file. (**Warning: `DO NOT UPLOAD THIS CONFIGURATION FILE ONLINE`**)

-   Install MySQL server and set up a database instance to store the downloaded tweets. For example `CREATE DATABASE twitter_db;`

-   Based on the [Twitter documentation](https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/intro-to-tweet-json) online, we create a TABLE with the following sample schema present in `twitter_sent_analysis/sql/TWEETS_BY_KEYWORD_schema.sql` for downloading tweets by keyword. The sample schema for downloading tweets by userid are present in `twitter_sent_analysis/sql/TWEETS_BY_USERID_schema.sql`:

```sql
CREATE TABLE TWEETS_BY_KEYWORD (
    ID INT AUTO_INCREMENT,
    tweet_id VARCHAR(255) NOT NULL,
    tweet TEXT NOT NULL,
    created_at VARCHAR(50),
    tweet_place VARCHAR(255),     /* Nullable object */
    favorite_count INT(11),       /* Nullable object */
    retweet_count INT(11) NOT NULL,
    reply_count INT(11) NOT NULL,

    user_name VARCHAR(255) NOT NULL,
    user_location VARCHAR(255),   /* Nullable object */
    user_followers_count INT(11) NOT NULL,
    user_friends_count INT(11) NOT NULL,
    PRIMARY KEY (ID)
);
```

-   The table creation SQL command can loaded into `twitterdb` using:

```shell
$ mysql -u root -p twitter_db < TWEETS_BY_KEYWORD_schema.sql;
$ mysql -u root -p twitter_db < TWEETS_BY_USERID_schema.sql;
```

## Run

### 1. To download latest tweets as zipped JSON files based on keyword, userid or geolocation

Make sure the `Twitter` secret keys and tokens are set up in `twitter_configuration.ini`.

From inside the `twitter_sent_analysis` directory, run:

```shell
$ python download_tweets_data_as_json.py [-FLAG] [FILENAME]
```

`-FLAG` can be set to `-t` for `keyword` search `-f` for `userid` search and `-l` for location search.

The input files should be a files containing the search terms in each line seperated by newline chars. (i.e. see `inputs/keywords.txt`)

**Example:**

-   To download latest tweets based on keywords from `inputs/keywords.txt`:

```shell
$ python download_tweets_data_as_json.py -t inputs/keywords.txt
```

### 2. To download latest tweets into MySQL based on keyword, userid or geolocation

Make sure the `MYSQL_TABLE` is set to the correct table for the `download_type`. i.e. For downloading using keyword filters, inside `twitter_configuration.ini`, set `TABLE` to `TWEETS_BY_KEYWORD` or the relevant table.

From inside the `twitter_sent_analysis` directory, run:

```shell
$ python download_tweets_data_to_mysql.py [-FLAG] [FILENAME]
```

**Note:**

-   To get help, run:

```shell
$ python download_tweets_data_to_mysql.py -h
```

`-FLAG` can be set to `-t` for `keyword` search `-f` for `userid` search and `-l` for location search.

The input files should be a files containing the search terms in each line seperated by newline chars. (i.e. see `inputs/keywords.txt`)

**Example:**

-   To download latest tweets based on keywords from `inputs/keywords.txt`:

```shell
$ python download_tweets_data_to_mysql.py -t inputs/keywords.txt
```

-   To download latest tweets based on userids from `inputs/userids.txt`:

```shell
$ python download_tweets_data_to_mysql.py -f inputs/userids.txt
```

-   To download latest tweets based on geolocations from `inputs/locations.txt`:

```shell
$ python download_tweets_data_to_mysql.py -l inputs/locations.txt
```

-   Filters can be combined as well. To download latest tweets based on userids from `inputs/userids.txt` and keywords from `inputs/keywords.txt`:

```shell
$ python download_tweets_data_to_mysql.py -f inputs/userids.txt -t inputs/keywords.txt
```

For more documentation: go to the [Twitter Streaming API documentation page](https://developer.twitter.com/en/docs/tweets/filter-realtime/guides/basic-stream-parameters)

### 3. Sentiment analysis on the downloaded tweets in the MySQL database

After the tweets have been loaded into the MySQL database, the `gen_tweets_sentiment_from_mysql.py` can generate a tweets csv file, sentiment results, and a wordcloud based on word-frequency.

#### Generating the sentiment analysis

```shell
$ python gen_tweets_sentiment_from_mysql.py -sent
```

#### Generating the csv tweet file

```shell
$ python gen_tweets_sentiment_from_mysql.py -csv [csv_filename]
```

#### Generating the word cloud

```shell
$ python gen_tweets_sentiment_from_mysql.py -wc [wc_filename]
```

**Note:** The flag options can be used together as well:

To generate sentiment, the word cloud and the csv tweet file:

```shell
$ python gen_tweets_sentiment_from_mysql.py -wc [wc_filename] -csv [csv_filename] - sent
```

**Sample wordcloud from tweets downloaded based on keywords 'batman' and 'joker'.**

<p align='center'>
<img src='img/batman_joker_tweets_word_cloud.jpg' />
</p>

#### Cleaning the Tweet data

Preprocessing steps for Natural Language Processing

1.  **Normalization** Convert all words to lowercase. Remove single chars which do not give much information

2.  **Removing extraneous information** Remove stop words (i, the, a, an, nltk library has a decent list), punctuation, diacritical marks, and HTML

3.  **Tokenization** Convert text into tokens using TextBlob

4.  **Lemmatisation** Convert words to their canonical form (i.e. eating and ate to eat)

5.  **Term Frequency-Inverse Document Frequency (TF-IDF)** Checking importance of words based on Frequency across main document or other multiple documents

We pass our pre-processed text into the TextBlob class and run the `sentiment.polarity` method of the object to a get a sentiment scores between -1 and 1 that can be converted to integers -1, 0, or 1 signalling a negative, neutral, or positive sentiment respectively.

## ETL pipeline for sentiment analysis of Rotten Tomatoes Movie Reviews

**Data Description**

The dataset is comprised of `tsv` files with phrases from the Rotten Tomatoes dataset. Sentences have been shuffled from their original order. Each Sentence has been parsed into many phrases by the Stanford parser. Each phrase has a `PhraseId`. Each sentence has a `SentenceId`. Phrases that are repeated (such as short/common words) are only included once in the data.

`train.tsv` contains the phrases and their associated sentiment labels. SentenceId can be used to track which phrases belong to a single sentence.
We attempt to assign a sentiment label to each phrase in `test.tsv` which contains just phrases.

The sentiment labels are:

-   0 negative
-   1 somewhat negative
-   2 neutral
-   3 somewhat positive
-   4 positive

### Requirements

-   python dependencies from `requirements.txt`

### Setup

### Run

#### Run sentiment analysis from previously downloaded RT reviews from Kaggle

With the `venv` activated, from inside the `rotten_tomatoes_movie_reviews_sent_analysis` directory, run:

```shell
$ python gen_rt_review_sentiment.py
```

#### Acknowledgements

-   [Kaggle Competition Sentiment Analysis on Movie Reviews](https://www.kaggle.com/c/sentiment-analysis-on-movie-reviews/)
-   [Daniel Foley](https://www.linkedin.com/in/daniel-foley-1ab904a2/)
