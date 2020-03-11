import re
import os
import pandas as pd

from textblob import TextBlob
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

import nltk
nltk.download('stopwords')
nltk.download('wordnet')


class MovieReviewObject:

    def __init__(self):
        self.review_data = pd.DataFrame()

    def get_df_from_file(self, data_file, sep='\t'):
        return pd.read_csv('data/train.tsv',
                           sep='\t',
                           header=0)

    def preprocess(self, review_df):
        ''' lowercase, remove non-alnum chars, remove stop words, and lemmatize '''
        stopwords_set = set(stopwords.words('english'))
        wordnet_lemmatizer = WordNetLemmatizer()

        def normalize(word):
            return ' '.join([wordnet_lemmatizer.lemmatize(
                word) for word in word.lower().split() if word not in stopwords_set])

        phrase_col_name = 'Phrase'
        review_df['cleanPhrase'] = review_df[phrase_col_name]
        exclude = ['[^a-zA-Z0-9]']
        exclude = '|'.join(exclude)

        review_df['cleanPhrase'].replace(
            to_replace=exclude, value=" ", regex=True, inplace=True)

        review_df['cleanPhrase'] = review_df['cleanPhrase'].apply(normalize)

        return review_df

    def generate_sentiment(self, text):
        text_analysis = TextBlob(text)
        negative_bound = -0.3
        positive_bound = 0.3
        neutral = 0
        polarity = text_analysis.sentiment.polarity
        if polarity > positive_bound:
            return 4   # postive
        if neutral < polarity < positive_bound:
            return 3   # somewhat postive
        elif polarity == neutral:
            return 2   # neutral
        elif neutral > polarity > negative_bound:
            return 1   # somewhat negative
        else:
            return 0   # negative


def main():
    rotrev = MovieReviewObject()
    rotrev_df = rotrev.get_df_from_file('data/train.tsv')
    rotrev_df = rotrev.preprocess(rotrev_df)

    rotrev_df['sentiment'] = rotrev_df['cleanPhrase'].apply(
        rotrev.generate_sentiment)

    rotrev_df['Correct'] = (rotrev_df['sentiment'] == rotrev_df['Sentiment'])
    rotrev_df_value_counts = rotrev_df['Correct'].value_counts()
    print(
        f"Accuracy ={rotrev_df_value_counts[True] / (rotrev_df_value_counts[True]+rotrev_df_value_counts[False])}")


if __name__ == "__main__":
    main()
