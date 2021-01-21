"""
    Function utils for Natural Language Processing.
"""

import re

import numpy as np
from stop_words import get_stop_words
from textblob import Textblob

STOP_WORDS_LIST_EN = get_stop_words("english")
STOP_WORDS_LIST_SP = get_stop_words("spanish")

### Add extra stop words for special cases
EXTRA_STOP_WORDS = []

STOP_WORDS_LIST = STOP_WORDS_LIST_EN+STOP_WORDS_LIST_SP+EXTRA_STOP_WORDS

def clean_tweet(txt):
    """
        Function that cleans tweets removing hashtags, retweets and urls.
    """
    txt = re.sub(r'@[A-Za-z0-9_]+', '', txt)
    txt = re.sub(r'#', '', txt)
    txt = re.sub(r'RT : ', '', txt)
    txt = re.sub(r'https?:\/\/[A-Za-z0-9\.\/]+', '', txt)
    return txt

def drop_stop_words(txt, stop_words_list=STOP_WORDS_LIST):
    """
        Function that drops the most repeated words for a given purpose.
    """
    splitted_txt = str(txt).split()
    result_split_txt = [word for word in splitted_txt if word not in stop_words_list]
    result_txt = ' '.join(result_split_txt)
    return result_txt

def get_subjectivity(txt):
    """
        Getting Subjectivity using Textblob.
    """
    return TextBlob(txt).sentiment.subjectivity

def get_polarity(txt):
    """
        Getting Polarity using TextBlob.
    """
    return TextBlob(txt).sentiment.polarity

def get_score(polarity):
    """
        Assings Score depending on Polarity.
    """
    if polarity < 0:
        return "Negative"
    elif polarity == 0:
        return "Neutral"
    else:
        return "Positive"
