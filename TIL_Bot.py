#! /usr/bin/env python3
import json
from urllib.request import urlopen,  Request
import tweepy
import time
from tweepy.parsers import JSONParser
import re
import Keys
import html
from pymongo import MongoClient

#  Authenticate twitter account
def _twit_auth():
    consumer_key = Keys.consumer_key
    consumer_secret = Keys.consumer_secret
    access_key = Keys.access_key
    access_secret = Keys.access_secret
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth, parser=JSONParser())

    return api

#  Pulls JSON data for the front page of TIL
def get_hot_TIL():

    url = 'https://www.reddit.com/r/todayilearned/hot/.json'
    hed = { 'User-Agent' : 'a bot to pull hot TIL facts by /u/yetep'}
    req = Request(url,  headers=hed)
    dict = json.loads(urlopen(req).read().decode('utf-8'))

    return dict

#  Parse the JSON and return a dictionary with the score, the post ID, and the title
def parse_TIL_data(data):
      
    parsed_data = []
      
    for post in data['data']['children']:
        if post['data']['author'] != 'TILMods':
            parsed_data.append({'score':post['data']['score'],  'title':html.unescape(post['data']['title']),  'id':post['data']['id'], 'url':post['data']['url']})
          
    return parsed_data

#  Formats the title for readibility
def _format_title(msg):

    _strip = re.compile(r'TIL( )?(:|,|.|...)? (of|that|That|Of|-)?(,)?( )?')
    _tostrip = _strip.search(msg['title'])

    try:
        TIL = msg['title'].replace(_tostrip.group(), '')
    except AttributeError:
        TIL = msg['title']

    if TIL[-1] != '.' and TIL[-2:] != '."' and TIL[-1] != '!' and TIL[-2:] != '!"':
        TIL = TIL + '.'

    if TIL[0] == '"':
        TIL = TIL[0] + TIL[1].capitalize() + TIL[2:]
    else:
        TIL = TIL[0].capitalize() + TIL[1:]

    return TIL

#  Post a message to Twitter    
def post_to_twitter(content):
    if len(content) < 141:
        _twit_auth().update_status(content)
        time.sleep(5)
    if len(content) > 140 and len(content) < 260:
        lfs = 120
        while True:
            if content[lfs] == ' ':
                break
            else:
                lfs = lfs + 1
        msg_list = [content[0:lfs], content[(lfs + 1):]]
        _twit_auth().update_status(msg_list[0])
        time.sleep(5)
        auth = _twit_auth()
        tweet = auth.user_timeline(id=auth.me(), count=1)[0]['id']
        _twit_auth().update_status(msg_list[1], tweet)
        time.sleep(5)

def main():
 
    _get_reddit_data = get_hot_TIL()
    _parse_reddit_data = parse_TIL_data(_get_reddit_data)

    dbclient = MongoClient('localhost', 27017)
    db = dbclient.TIL_Posts

    for post in _parse_reddit_data:
        if post['score'] > 1000 and db.posts.find({"id": post['id']}).count() == 0:
            TILPost = _format_title(post)
            db_data = {'id': post['id'], 'post':TILPost, 'url':post['url']}
            db.posts.insert_one(db_data).inserted_id
            post_to_twitter(TILPost)
          
if __name__ == '__main__':
    main()
