#!/usr/bin/env python
# coding: utf-8

# In[1]:


from tweepy import API
from tweepy import Cursor
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import CREDENTIALS


# In[2]:


# # # # TWITTER CLIENT # # # #
class TwitterClient():
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)

        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client

    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets

    def get_friend_list(self, num_friends):
        friend_list = []
        for friend in Cursor(self.twitter_client.friends, id=self.twitter_user).items(num_friends):
            friend_list.append(friend)
        return friend_list

    def get_home_timeline_tweets(self, num_tweets):
        home_timeline_tweets = []
        for tweet in Cursor(self.twitter_client.home_timeline, id=self.twitter_user).items(num_tweets):
            home_timeline_tweets.append(tweet)
        return home_timeline_tweets


# In[3]:


# # # # TWITTER AUTHENTICATER # # # #
class TwitterAuthenticator():

    def authenticate_twitter_app(self):
        auth = OAuthHandler(CREDENTIALS.CONSUMER_KEY,
                            CREDENTIALS.CONSUMER_SECRET)
        auth.set_access_token(CREDENTIALS.ACCESS_TOKEN,
                              CREDENTIALS.ACCESS_TOKEN_SECRET)
        return auth


# In[4]:


# # # # TWITTER STREAMER # # # #
class TwitterStreamer():
    """
    Class for streaming and processing live tweets.
    """

    def __init__(self):
        self.twitter_autenticator = TwitterAuthenticator()

    def stream_tweets(self, fetched_tweets_filename, hash_tag_list):
        # This handles Twitter authetification and the connection to Twitter Streaming API
        listener = TwitterListener(fetched_tweets_filename)
        auth = self.twitter_autenticator.authenticate_twitter_app()
        stream = Stream(auth, listener)

        # This line filter Twitter Streams to capture data by the keywords:
        stream.filter(track=hash_tag_list)


# In[5]:


# # # # TWITTER STREAM LISTENER # # # #
class TwitterListener(StreamListener):
    """
    This is a basic listener that just prints received tweets to stdout.
    """

    def __init__(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename

    def on_data(self, data):
        try:
            print(data)
            with open(self.fetched_tweets_filename, 'a') as tf:
                tf.write(data)
            return True
        except BaseException as e:
            print("Error on_data %s" % str(e))
        return True

    def on_error(self, status):
        if status == 420:
            # Returning False on_data method in case rate limit occurs.
            return False
        print(status)


# In[6]:


class TweetAnalyser():

    def tweets_to_data_frame(self, tweets):
        df = pd.DataFrame(
            data=[tweet.text for tweet in tweets], columns=['text'])

        df['created_at'] = np.array([tweet.created_at for tweet in tweets])
        df['id'] = np.array([tweet.id for tweet in tweets])
        df['in_reply_to_screen_name'] = np.array(
            [tweet.in_reply_to_screen_name for tweet in tweets])
        df['in_reply_to_status_id'] = np.array(
            [tweet.in_reply_to_status_id for tweet in tweets])
        df['in_reply_to_user_id'] = np.array(
            [tweet.in_reply_to_user_id for tweet in tweets])
        # df['retweeted_id'] = np.array([tweet.retweeted_id for tweet in tweets])
        # df['retweeted_screen_name'] = np.array(
        # [tweet.retweeted_screen_name for tweet in tweets])
        # df['user_mentions_screen_name'] = np.array(
        #     [tweet.user_mentions_screen_name for tweet in tweets])
        # df['user_mentions_id'] = np.array(
        #     [tweet.user_mentions_id for tweet in tweets])
        # df['user_id'] = np.array([tweet.user_id for tweet in tweets])
        # df['screen_name'] = np.array([tweet.screen_name for tweet in tweets])
        df['retweet_count'] = np.array(
            [tweet.retweet_count for tweet in tweets])

        return df

    def clean_tweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())


# In[7]:


if __name__ == '__main__':
    twitter_client = TwitterClient()
    tweet_analser = TweetAnalyser()
    api = twitter_client.get_twitter_client_api()

    tweets = api.user_timeline(screen_name="Infosys", count=20)
    print(dir(tweets[0]))
    df = tweet_analser.tweets_to_data_frame(tweets)

    print(df.head())
    # # Time series of retweets
    # time_retweets = pd.Series(data=df['retweets'].values, index=df['date'])
    # time_retweets.plot(figsize=(16, 4), label="retweets", legend=True)

    # time_like = pd.Series(data=df['likes'].values, index=df['date'])
    # time_like.plot(figsize=(16, 4), label="likes", legend=True)

    # plt.show()


# In[ ]:
