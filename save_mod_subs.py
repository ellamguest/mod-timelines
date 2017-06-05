#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  2 14:23:59 2017

@author: emg
"""
import pandas as pd
import requests
import json
import time
from datetime import date
import os


def save_moderated_subreddits_json(user, subreddit):
    url = 'https://www.reddit.com/user/{}/moderated_subreddits.json'.format(user)
    r = requests.get(url, headers = {'user-agent':'ThisIsABot'})
    data = r.json()
    
    path = os.path.join('moding-data', '{}'.format(subreddit), str(date.today()), '{}.json'.format(user))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    with open(path, 'w') as f:
        json.dump(data, f)
    
    time.sleep(2)
    
    return data
      

def open_moderated_subreddits_json(user, subreddit):
    path = os.path.join('moding-data', '{}'.format(subreddit), str(date.today()), '{}.json'.format(user))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    with open(path, 'r') as f:
        data = json.load(f)
    
    return data
    

def json_to_df(data, user):
    '''data is a json objecy
    '''
    d = {}
    if 'data' in data:
        for item in data['data']:
            d[item['sr']] = item['subscribers']
    elif 'message' in data:
        print(data['message'])
        d[data['message']] = data['message']
    else:
        d[0] = 0
    
    df = pd.DataFrame.from_dict(d, orient='index')
    df.reset_index(inplace=True)
    df.rename(columns={0 : 'subscribers', 'index':'sub'}, inplace=True)
    df['name'] = user
    df['date'] = date.today()
    
    return df
    
 
def get_mod_type(df, user, mode=0):
    current = df['pubdate'].max()
    subset = df[df['name']==user]
    if mode == 0:
        return 0
    if current not in list(subset['pubdate']):
        if "['all']" not in list(subset['permissions']):
            return 1
        else:
            return 2
    if current in list(subset['pubdate']):
        if "['all']" not in list(subset['permissions']):
            return 3
        else:
            return 4
    else:
        return 'ERROR'    

def edgelist(subreddit, df):
    names = list(df['name'].unique())
    names.remove('AutoModerator')
    
    dfs = []
    n = len(names)
    print ('Getting current moderated subreddit lists for {} moderators'.format(subreddit))
    print()
    for name in names:
        print(n, name)
        data = save_moderated_subreddits_json(name, subreddit)
        df = json_to_df(data, name)
        dfs.append(df)
        n -= 1
    
    print('MAKING {} EDGELIST...'.format(subreddit))
    edgelist = pd.concat(dfs)
    edgelist.reset_index(drop=True, inplace=True)
    edgelist['sub'] = 'r/' + edgelist['sub'].astype('str')
    edgelist = edgelist[['name','sub','subscribers','date']]
    
    edgelist_path = os.path.join('moding-data', subreddit, str(date.today()), 'lists', 'edgelist.csv')
    os.makedirs(os.path.dirname(edgelist_path), exist_ok=True)
    edgelist.to_csv(edgelist_path, index=False)

    return edgelist


def nodelist(subreddit, edgelist, df):
    print('MAKING {} NODELIST...'.format(subreddit))
    d = {}
    d['name'] = list(set(edgelist['name'])) + list(set(edgelist['sub']))
    d['type'] = [1]*len(list(set(edgelist['name']))) + [0]*len(list(set(edgelist['sub'])))
    nodelist = pd.DataFrame.from_dict(d, orient='columns')
    nodelist['mod_type'] = nodelist.apply(lambda row: get_mod_type(df, row['name'], row['type']), axis=1)
    
    nodelist_path = os.path.join('moding-data', subreddit, str(date.today()), 'lists', 'nodelist.csv')
    os.makedirs(os.path.dirname(nodelist_path), exist_ok=True)
    nodelist.to_csv(nodelist_path, index=False)


def run(subreddit):
    #update modtimelines first
    # sub = 'cmv' or 'td
    master_path = os.path.join('mod-list-data', '{}'.format(subreddit), 'master.csv')
    master = pd.read_csv(master_path)
    print ()
    print()
    
    print()
    e = edgelist(subreddit, master)
    print()
    
    nodelist(subreddit, e, master)
    
def run_both():
    run('The_Donald')
    print()
    print()
    run('changemyview')

#
#names_path = os.path.join('mod-list-data', '{}'.format(subreddit), 'names.pkl')
#os.makedirs(os.path.dirname(names_path), exist_ok=True)
#names = list(set(master['name']))
#pickle.dump(names, open(names_path, "wb" ) )    
#n = pickle.load( open( names_path, "rb" ) )

