import datetime
from io import StringIO
import os
from time import perf_counter

import boto3
import matplotlib.pyplot as plt
import pandas as pd
from wordcloud import WordCloud

from settings.aws_settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
from utils import clean_tweet, get_subjectivity, get_polarity, get_score, drop_stop_words

plt.style.use("ggplot")

SESSION = boto3.Session(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
s3 = SESSION.resource('s3')
s3_client = SESSION.client("s3")

start = perf_counter()

print("Attempting to read tweets data")
tweet_data = pd.read_csv("data/out.csv", header=None)
tweet_data.columns = ["Date Created", "Text", "Location", 
                      "Retweet_Flag", "Quote FLag", "Place"]

print(f"Tweet data Shape:{tweet_data.shape}")

print("Showing first registers")

print(tweet_data.head())

print("\nAttempting to clean tweets")
tweet_data['Tweet'] = tweet_data['Text'].apply(clean_tweet)
tweet_data["Tweet"] =  tweet_data["Tweet"].apply(drop_stop_words)

print("\nAttempting to get Polarity and Subjectivity")
tweet_data['Subjectivity'] = tweet_data['Tweet'].apply(get_subjectivity)
tweet_data['Polarity'] = tweet_data['Tweet'].apply(get_polarity)

print("\nDropping empty rows")
tweet_data = tweet_data.drop(tweet_data[tweet_data['Tweet'] == ''].index)

print("\nComputing Sentiment Score\n")
tweet_data['Score'] = tweet_data['Polarity'].apply(get_score)

positive = tweet_data[tweet_data['Score'] == 'Positive']
negative = tweet_data[tweet_data['Score'] == 'Negative']
neutral = tweet_data[tweet_data['Score'] == 'Neutral']

print("\n##################################################################")
print("##################################################################")
print("Summary:\n")
print(f"{round(positive.shape[0]/(tweet_data.shape[0])*100, 6)} % of Positive tweets")
print(f"{round(neutral.shape[0]/(tweet_data.shape[0])*100, 6)} % of Neutral tweets")
print(f"{round(negative.shape[0]/(tweet_data.shape[0])*100, 6)} % of Negative tweets\n")
print("##################################################################")
print("##################################################################\n")

os.makedirs("results", exist_ok=True)
print("Plotting Score Distribution")
labels = tweet_data.groupby(['Score']).count().index.values
values = tweet_data.groupby(['Score']).size().values
plt.figure()
plt.bar(labels, values, color="darkred")
plt.title("Sentiment Score Distribution")
plt.savefig("results/plot.png")
plt.show()

print("Generatigng WordCloud\n")

words = ' '.join([tweet for tweet in tweet_data['Tweet']])
word_cloud = WordCloud(width=600, height=400).generate(words)

plt.imshow(word_cloud)
plt.axis("off")
plt.savefig(f"results/wordcloud_{datetime.date.today()}.png")
plt.show()

print(f"Boto3 Session:{SESSION}")

print("Attempting to save data into S3 bucket")
csv_buffer = StringIO()
tweet_data.to_csv(csv_buffer)

s3.Object("dg-twitter-test", f"raw_data_{datetime.date.today()}.csv").put(Body=csv_buffer.getvalue())
print("File Successfully Saved into S3!!!")

end = perf_counter()

print(f"The execution took a time of: {end - start} \n")

print("##################################################################")
print("##################################################################\n")