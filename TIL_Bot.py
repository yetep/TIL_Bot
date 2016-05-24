#! /usr/bin/env python3
import json
from urllib.request import urlopen,  Request
import datetime
import tweepy
import time

#  Pulls JSON data for the front page of TIL
def get_hot_TIL():
    url = 'https://www.reddit.com/r/todayilearned/hot/.json'
    hed = { 'User-Agent' : 'a bot to pull hot TIL facts by /u/yetep'}
    req = Request(url,  headers=hed)
    dict = json.loads(urlopen(req).readall().decode('utf-8'))
    return dict

#  Parse the JSON and return a dictionary with the score, the post ID, and the title
def parse_TIL_data(data):
      
    parsed_data = {'data':[]}
      
    for post in data['data']['children']:
        if post['data']['author'] != 'TILMods':
            parsed_data['data'].append({'score':post['data']['score'],  'title':post['data']['title'],  'id':post['data']['id']})
          
    return parsed_data

#  Authenticate twitter account
def _twit_auth():
    
    consumer_key = 'Your consumer key'
    consumer_secret = 'Your consumer secret'
    access_key = 'Your access key'
    access_secret = 'your access secret'
    auth = tweepy.OAuthHandler(consumer_key,  consumer_secret)
    auth.set_access_token(access_key,  access_secret)
    api = tweepy.API(auth)
    
    return api

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
        msg_list = [content[0:lfs] + ' (1/2)', content[(lfs + 1):] + ' (2/2)']
        for item in msg_list:
            _twit_auth().update_status(item)
            time.sleep(5)
    
def main():
 
    x = get_hot_TIL()
    y = parse_TIL_data(x)
    
    #  This opens the log of previous post ID's and creates a list of them to check against the new data pulled.  If the log does not exist the list is set to be emply
    try:
        open_id_archive = open('ID.log',  'rU')
        id_list = [id.strip('\n') for id in open_id_archive]
        open_id_archive.close()
    except FileNotFoundError:
        id_list = []
              
    log = open('TIL.log',  'a')
    id_log = open('ID.log',  'a')
     
    for post in y['data']:
        if post['score'] > 1000 and post['id'] not in id_list:
            TIL = post['title'].replace('TIL ',  '').replace('TIL: ',  '').replace('that ',  '',  1)
            if TIL[-1] != '.':
                TIL = TIL + '.'
            if TIL[0] == '"':
                msg = TIL[0] + TIL[1].capitalize() + TIL[2:]
                log.write(msg + '\n')
                post_to_twitter(msg)

            else:
                msg = TIL[0].capitalize() + TIL[1:]
                log.write(msg + '\n')
                post_to_twitter(msg)
              
            id_log.write(str(post['id']) + '\n')
                  
    log.write(str(datetime.datetime.now()) + '\n' + '\n')
    id_log.write(str(datetime.datetime.now()) + '\n' + '\n')
          
    log.close()
    id_log.close()
  
          
if __name__ == '__main__':
    main()
