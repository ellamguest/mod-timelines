#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  1 11:25:35 2017

@author: emg
"""

import requests
import pandas as pd
import time
from datetime import date
import os
import json

name = 'NYPD-32'
name = 'ohsnapyougotserved'

sub = 'td'
df = pd.read_csv('/Users/emg/Programming/GitHub/mod-timelines/tidy-data/{}-mod-hist.csv'.format(sub), index_col=0)

names = df['name'].unique()[:5]

### CREATE EDGELIST + NODELIST FUNCTIONS

def mod_list(name):
    #url = 'https://www.reddit.com/user/{}/moderated_subreddits.json'.format(name)
    #r = requests.get(url, {'user-agent':'ThisIsABot'})
    r = requests.get('https://www.reddit.com/user/{}/moderated_subreddits.json'.format(name), headers={'user-agent': 'ThisIsABot'})
    data = r.json()

    path = os.path.join('moding-data', '{}'.format(sub), str(date.today()), '{}'.format(name))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    with open(path, 'w') as f:
        json.dump(data, f)
    
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
    df['mod'] = name
    df['date'] = date.today()
    
    time.sleep(2)
      
    return df
 
def edgelist(sub):
    df = pd.read_csv('/Users/emg/Programming/GitHub/mod-timelines/tidy-data/{}-mod-hist.csv'.format(sub), index_col=0)
    names = df['name'].unique()
    
    dfs = []
    n = len(names)
    for name in names:
        print(n, name)
        dfs.append(mod_list(name))
        n -= 1
    
    edgelist = pd.concat(dfs)
    edgelist.reset_index(drop=True, inplace=True)
    
    edgelist_path = os.path.join('moding-data', '{}'.format(sub), str(date.today()), 'lists', 'edgelist')
    os.makedirs(os.path.dirname(edgelist_path), exist_ok=True)
    edgelist.to_csv(edgelist_path, index=False)

    
    return edgelist


def nodelist(sub, edgelist):
    df = pd.read_csv('/Users/emg/Programming/GitHub/mod-timelines/tidy-data/{}-mod-hist.csv'.format(sub), index_col=0)
    nodelist = pd.DataFrame(list(set(edgelist['mod'])) + list(set(edgelist['sub'])))
    modes = [1]*len(list(set(edgelist['mod']))) + [0]*len(list(set(edgelist['sub'])))
    nodelist['type'] = modes
    nodelist.rename(columns={0 : 'mod'}, inplace=True)
    nodelist['mod_types'] = nodelist.apply(lambda row: get_mod_type(df, row['mod'], row['type']), axis=1)
    
    nodelist_path = os.path.join('moding-data', '{}'.format(sub), str(date.today()), 'lists', 'nodelist')
    os.makedirs(os.path.dirname(nodelist_path), exist_ok=True)
    nodelist.to_csv(nodelist_path, index=False)

    return nodelist

sub = 'cmv'
edgelist = (sub)
nodelist = nodelist(sub, edgelist)
    

