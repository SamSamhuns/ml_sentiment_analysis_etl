CREATE TABLE TWEETS (
    ID INT AUTO_INCREMENT,
    tweet_id VARCHAR(255) NOT NULL,
    tweet TEXT NOT NULL,
    created_at VARCHAR(50),
    tweet_place VARCHAR(255),   /* Nullable object */
    favorite_count INT(11),       /* Nullable object */
    retweet_count INT(11) NOT NULL,
    reply_count INT(11) NOT NULL,

    user_name VARCHAR(255) NOT NULL,
    user_location VARCHAR(255), /* Nullable object */
    user_followers_count INT(11) NOT NULL,
    user_friends_count INT(11) NOT NULL,
    PRIMARY KEY (ID)
);
