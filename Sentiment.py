'''
Created on Aug 2, 2017

@author: tyler reece
'''

import collections
import json
import re
import operator
import string
import math
import csv
import nltk
from collections import defaultdict
from collections import Counter
from nltk.corpus import stopwords
from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer
from nltk.tbl import feature

#start replaceTwoOrMore
def replaceTwoOrMore(s):
    #look for 2 or more repetitions of character and replace with the character itself
    pattern = re.compile(r"(.)\1{1,}", re.DOTALL)
    return pattern.sub(r"\1\1", s)
#end
 
#start getStopWordList
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
#end

#start getfeatureVector
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
#end

def preprocess(tweet):
    # process the tweets

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

#start extract_features
def extract_features(tweet):
    tweet_words = set(tweet)
    features = {}
    print featureList
    for word in featureList:
        features['contains(%s)' % word] = (word in tweet_words)
    print features
    return features
#end

stopWords = getStopWordList('stopwords.txt')
featureList = []
tweets = []

with open('positive_words.txt', 'r') as positiveFile:
    positiveSentiment = 'positive'
    #positiveFeatureVector = positiveFile.read().split(',')
    positiveWords = 'good,nice,cool,yummy'
    positiveFeatureVector = positiveWords.split(',')
    featureList.extend(positiveFeatureVector)
    tweets.append((positiveFeatureVector, positiveSentiment));

with open('negative_words.txt', 'r') as negativeFile:
    neutralSentiment = 'neutral'
    #negativeFeatureVector = negativeFile.read().split(',')
    neutralWords = 'okay,sure,wtf'
    neutralFeatureVector = neutralWords.split(',')
    featureList.extend(neutralFeatureVector)
    tweets.append((neutralFeatureVector, neutralSentiment));

with open('negative_words.txt', 'r') as negativeFile:
    negativeSentiment = 'negative'
    #negativeFeatureVector = negativeFile.read().split(',')
    negativeWords = 'bad,mean,nasty'
    negativeFeatureVector = negativeWords.split(',')
    featureList.extend(negativeFeatureVector)
    tweets.append((negativeFeatureVector, negativeSentiment));

print tweets     
# Extract feature vector for all tweets in one shot
training_set = nltk.classify.util.apply_features(extract_features, tweets)

# Train the classifier
NBClassifier = nltk.NaiveBayesClassifier.train(training_set)

# Test the classifier
testTweet = 'good nice cool happy'
processedTestTweet = preprocess(testTweet) 

#print processedTestTweet
#print extract_features(getFeatureVector(processedTestTweet))

#print extract_features(getFeatureVector(testTweet))  
print NBClassifier.classify(extract_features(processedTestTweet))
#print 'Features'
#print features
#print 'feature list' 
#3print featureList
#print 'tweets'
#print tweets
