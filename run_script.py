#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 22 14:34:45 2017

@author: emg
"""

import pandas as pd
import requests
import json
from datetime import date
import os
import time

def update_mod_list(subreddit, name):
    '''master copy of mod-list must exist at
    'moding-data/{sub}/master.csv'
    
    subreddit = 'cmv' or 'td'
    name = 'changemyview' or 'The_Donald'
    '''
    print('Opening master of {} mod history'.format(name))
    master_path = os.path.join('moding-data', '{}'.format(subreddit), 'master.csv')
    master = pd.read_csv(master_path)
    
    print('Getting current mod list for {}'.format(name))
    url = 'https://www.reddit.com/r/{}/about/moderators.json'.format(name)
    r = requests.get(url, headers={'user-agent':'why_ask_reddit-Bot'})
    data = r.json()
    
    mod_list_path = os.path.join('moding-data', '{}'.format(subreddit), str(date.today()), '{}.json'.format(str(date.today())))
    os.makedirs(os.path.dirname(mod_list_path), exist_ok=True)
    
    with open(mod_list_path, 'w') as f:
        json.dump(data, f)
    
    print('Updating master of {} mod history'.format(subreddit))
    d = {}
    for c in data['data']['children']:
        d[c['name']] = [c['date'], c['mod_permissions'], c['author_flair_text']]
    
    df = pd.DataFrame.from_dict(d, orient='index')
    df.reset_index(inplace=True)
    df.head()
    df.rename(columns={'index':'name', 0:'date', 1:'permissions', 2:'author_flair_text'}, inplace=True)
    df['date'] = pd.to_datetime(df['date'], unit='s')
    df['pubdate'] = date.today()
    df.head()
    
    updated = pd.concat([master,df])
    updated.reset_index(drop=True, inplace=True)
    updated.to_csv(master_path, index=False)
  
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
    
def edgelist(subreddit, subname, df):
    names = list(df['name'].unique())
    names.remove('AutoModerator')
    
    dfs = []
    n = len(names)
    print ('Getting current moderated subreddit lists for {} moderators'.format(subname))
    print()
    for name in names:
        print(n, name)
        data = save_moderated_subreddits_json(name, subreddit)
        df = json_to_df(data, name)
        dfs.append(df)
        n -= 1
    
    print('MAKING {} EDGELIST...'.format(subname))
    edgelist = pd.concat(dfs)
    edgelist.reset_index(drop=True, inplace=True)
    edgelist['sub'] = 'r/' + edgelist['sub'].astype('str')
    edgelist = edgelist[['name','sub','subscribers','date']]
    
    edgelist_path = os.path.join('moding-data', subreddit, str(date.today()), 'lists', 'edgelist.csv')
    os.makedirs(os.path.dirname(edgelist_path), exist_ok=True)
    edgelist.to_csv(edgelist_path, index=False)

    return edgelist

def get_mod_type(df, user, mode=0):
    df = df.head(20)
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

def nodelist(subreddit, subname, edgelist, df):
    print('MAKING {} NODELIST...'.format(subname))
    d = {}
    d['name'] = list(set(edgelist['name'])) + list(set(edgelist['sub']))
    d['type'] = [1]*len(list(set(edgelist['name']))) + [0]*len(list(set(edgelist['sub'])))
    nodelist = pd.DataFrame.from_dict(d, orient='columns')
    nodelist['mod_type'] = nodelist.apply(lambda row: get_mod_type(df, row['name'], row['type']), axis=1)
    
    nodelist_path = os.path.join('moding-data', subreddit, str(date.today()), 'lists', 'nodelist.csv')
    os.makedirs(os.path.dirname(nodelist_path), exist_ok=True)
    nodelist.to_csv(nodelist_path, index=False)


def run_subreddit(subreddit, subname):
    #update modtimelines first
    # sub = 'cmv' or 'td
    update_mod_list(subreddit, subname)
    master_path = os.path.join('moding-data', '{}'.format(subreddit), 'master.csv')
    master = pd.read_csv(master_path)
    print ()
    print()
    
    print()
    e = edgelist(subreddit, subname, master)
    print()
    
    nodelist(subreddit, subname, e, master)
    
def run():
    #run_subreddit('td', 'The_Donald')
    #time.sleep(2)
    print()
    print()
    run_subreddit('cmv', 'changemyview')    