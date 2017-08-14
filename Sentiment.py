'''
Created on Aug 2, 2017
@author: tyler reece
'''

import json
import re
import csv
import nltk
import tweepy
import time
import pickle
import codecs
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener
from datetime import datetime

# keys and tokens from the Twitter Dev Console
consumer_key = ''
consumer_secret = ''
access_token = ''
access_secret = ''

#start replaceTwoOrMore
def replaceTwoOrMore(s):
    #look for 2 or more repetitions of character and replace with the character itself
    pattern = re.compile(r"(.)\1{1,}", re.DOTALL)
    return pattern.sub(r"\1\1", s)
#end
 
def getStopWordList(stopWordListFileName):
    #read the stopwords file and build a list
    stopWords = []
    stopWords.append('AT_USER')
    stopWords.append('URL')

    with open(stopWordListFileName, 'r') as stopList:
        line = stopList.readline()
        while line:
            word = line.strip()
            stopWords.append(word)
            line = stopList.readline()
    return stopWords

stopWords = getStopWordList('stopwords.txt')

def getFeatureVector(tweet):
    featureVector = []
    #split tweet into words
    words = tweet.split()
    for w in words:
        #replace two or more with two occurrences
        w = replaceTwoOrMore(w)
        #strip punctuation
        w = w.strip('\'"?,.')
        #check if the word stats with an alphabet
        val = re.search(r"^[a-zA-Z][a-zA-Z0-9]*$", w)
        #ignore if it is a stop word
        if(w in stopWords or val is None):
            continue
        else:
            featureVector.append(w.lower())
    return featureVector

def processTweet(tweet):
    #Convert to lower case
    tweet = tweet.lower()
    #Convert www.* or https?://* to URL
    tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))','URL',tweet)
    #Convert @username to AT_USER
    tweet = re.sub('@[^\s]+','AT_USER',tweet)
    #Remove additional white spaces
    tweet = re.sub('[\s]+', ' ', tweet)
    #Replace #word with word
    tweet = re.sub(r'#([^\s]+)', r'\1', tweet)
    #trim
    tweet = tweet.strip('\'"')
    return tweet

def extract_features(tweet):
    tweet_words = set(tweet)
    features = {}
    for word in featureList:
        features['contains(%s)' % word] = (word in tweet_words)
    return features

featureList = []
tweets = []

print ('Training classfier.....')
print str(datetime.now())

inpTweets = csv.reader(open('2kTestSet.csv', 'rU'), delimiter=',', quotechar='|')

for row in inpTweets:
    sentiment = row[0];
    tweet = row[1]
    processedTweet = processTweet(tweet)
    featureVector = getFeatureVector(processedTweet)
    featureList.extend(featureVector)
    tweets.append((featureVector, sentiment));

# Extract feature vector for all tweets in one shot
training_set = nltk.classify.util.apply_features(extract_features, tweets)
# Train the classifier
NBClassifier = nltk.NaiveBayesClassifier.train(training_set)
#f = open('my_classifier_20k.pickle', 'wb')
#pickle.dump(NBClassifier, f)
#f.close()

#print ('classifier stored as my_classifier.pickle')
#f = open('my_classifier_10k.pickle', 'rb')
#NBClassifier = pickle.load(f)
#f.close()

print ('Classifier loaded. Now classifying tweets.')
print str(datetime.now())

#Twitter streaming start ------------------------------------------------------------------------
# attempt authentication
try:
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
     
    api = tweepy.API(auth)
except:
    print("Error: Authentication Failed")
 
class MyListener(StreamListener):
    
    def __init__(self, time_limit=600):
        self.start_time = time.time()
        self.limit = time_limit
        self.saveFile = open('TweetSentiment.csv', 'a')
        super(StreamListener, self).__init__()
    
    def on_connect(self):
        print('Connected to Stream')
        pass
 
    def on_data(self, data):
        try:
            tweet = json.loads(data)
            if (time.time() - self.start_time) < self.limit:
                if 'text' in tweet:
                    processedTweet = processTweet(tweet['text']) 
                    tweetSentiment = NBClassifier.classify(extract_features(getFeatureVector(processedTweet)))
                    print tweetSentiment
                else:
                    processedTweet = 'no tweet'
                    tweetSentiment = 'none'
                if 'id_str' in tweet:
                        idStr = tweet['id_str']
                else:
                     idStr = 'none'
                        
                if 'created_at' in tweet:
                    createdAt = tweet['created_at']
                else:
                     createdAt = 'none'
                        
                if 'favorite_count' in tweet:
                    favoriteCount = tweet['favorite_count']
                else:
                    favoriteCount = 'none'
                        
                if 'retweeted_count' in tweet:
                    retweetedCount = tweet['retweeted_count']
                else:
                    retweetedCount = 'none'
                        
                if 'user' in tweet:
                    user = tweet['user']
                    if 'screen_name' in user:
                        screenName = user['screen_name']
                    else:
                        screenName = 'none'
                    if 'statuses_count' in user:
                        statusesCount = user['statuses_count']
                    else:
                        statusesCount = 'none'
                    if 'followers_count' in user:
                        followersCount = user['followers_count']
                    else:
                        followersCount = 'none'
                    if 'location' in user:
                        location = user['location']
                    else:
                        location = 'none'
                    if 'lang' in user:
                        language = user['lang']
                    else:
                        language = 'none'
                else:
                    user = 'none'
                
                self.saveFile.write(tweetSentiment)
                self.saveFile.write('|')
                self.saveFile.write(str(idStr).encode("utf-8"))
                self.saveFile.write('|')
                self.saveFile.write(processedTweet.encode("utf-8"))
                self.saveFile.write('|')
                self.saveFile.write(str(screenName).encode("utf-8"))
                self.saveFile.write('|')
                self.saveFile.write(str(createdAt).encode("utf-8"))
                self.saveFile.write('|')
                self.saveFile.write(str(favoriteCount).encode("utf-8"))
                self.saveFile.write('|')
                self.saveFile.write(str(retweetedCount).encode("utf-8"))
                self.saveFile.write('|')
                self.saveFile.write(str(statusesCount).encode("utf-8"))
                self.saveFile.write('|')
                self.saveFile.write(str(followersCount).encode("utf-8"))
                self.saveFile.write('|')
                self.saveFile.write(str(location).encode("utf-8"))
                self.saveFile.write('|')
                self.saveFile.write(str(language).encode("utf-8"))
                self.saveFile.write('|')
                self.saveFile.write('\n')
                return True
            else:
                self.saveFile.close()
                print('Stream complete!')
                return False

        except BaseException as e:
                print("Error on_data: %s" % str(e))        
        return True
 
    def on_error(self, status):
        print(status)
        return True
 
 #change these to stream whatever filter you want
twitter_stream = Stream(auth, MyListener())
twitter_stream.filter(track=['#zeke' , '#zekeelliott', '#EzekielElliott', '#cowboys', '#NFL', '#dallascowboys', '#football'])

#Twitter streaming end ------------------------------------------------------------------------
            
print 'Sentiment complete'
print str(datetime.now())
#print extract_features(getFeatureVector(testTweet))  
#print NBClassifier.classify(extract_features(getFeatureVector(processedTestTweet)))