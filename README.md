# Extract Transform Load Data Pipelines for sentiment analysis

-   [Twitter feed ETL sentiment analysis based on keyword search.](#data-pipeline-for-sentiment-analysis-of-twitter-feeds)
-   [IMDB movie critic review sentiment analysis based on movie genre.](#etl-pipeline-for-analysis-of-imdb-movie-critic-reviews)

## General setup

-   Make sure Python is installed and set up a Python virtualenv. Install all dependencies from `requirements.txt`.

```shell
$ pip install virtualenv
$ virtualenv venv/bin/activate
$ source venv/bin/activate
$ pip install -r requirements.txt
```

## ETL pipeline for sentiment analysis of Twitter feeds

Download tweets with twitter api, load in an MySQL db, and analyze tweet sentiments all in an ETL pipeline.

### Requirements

-   Twitter account and API credentials (Access Token from a Twitter app)
-   MySQL database server

### Setup

-   Add the required `CONSUMER_KEY`, `CONSUMER_SECRET`, `ACCESS_TOKEN`, `ACCESS_TOKEN_SECRET` and `MYSQL_PASSWORD` to the `tweet_sentiment_analysis/configuration.ini` file. (**Warning: `DO NOT UPLOAD THIS CONFIGURATION FILES ONLINE`**)

-   Install MySQL server and set up a database instance to store the downloaded tweets. For example `CREATE DATABASE twitter_db;`

-   Based on the [Twitter documentation](https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/intro-to-tweet-json) online, we create a TABLE with the following sample schema present in `TWEETS_schema.sql`:

```sql
CREATE TABLE TWEETS (
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
$ mysql -u root -p twitter_db < TWEETS_schema.sql;
```

### Run

## ETL pipeline for analysis of IMDB movie critic reviews

### Requirements

### Setup

### Run

#### Acknowledgements

-   [Daniel Foley](https://www.linkedin.com/in/daniel-foley-1ab904a2/)
