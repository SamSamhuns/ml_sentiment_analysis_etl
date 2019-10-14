# Data pipeline for sentiment analysis of Twitter feeds

A data pipeline project to download tweets with twitter api, load in an MySQL db, and analyze tweet sentiments all in an ETL pipeline.

## Requirements

-   Twitter account and API credentials (Access Token from a Twitter app)
-   MySQL database server

## Setup

-   Add the required `CONSUMER_KEY`, `CONSUMER_SECRET`, `ACCESS_TOKEN`, `ACCESS_TOKEN_SECRET` and `MYSQL_PASSWORD` to the `configuration.ini` file. (**Warning: `DO NOT UPLOAD YOUR CONFIGURATION FILES ONLINE`**)

-   Install MySQL server and set up a database instance to store the downloaded tweets. For example `CREATE DATABASE twitter_db;`

-   Based on the [Twitter documentation](https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/intro-to-tweet-json) online, we create a TABLE with the following sample schema in `TWEETS_schema.sql`:

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

-   The creation command can loaded into `twitterdb` using `mysql -u root -p twitter_db < TWEETS_schema.sql`.


#### Acknowledgements

-   [Daniel Foley](https://www.linkedin.com/in/daniel-foley-1ab904a2/)
