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

def new_layout(name):
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
    else:
        print(data['message'])
        d[data['message']] = data['message']
    
    df = pd.DataFrame.from_dict(d, orient='index')
    df.reset_index(inplace=True)
    df.rename(columns={0 : 'subscribers', 'index':'sub'}, inplace=True)
    df['mod'] = name
    
    time.sleep(2)
      
    return df
 
sub = 'cmv'
def run(sub):
    df = pd.read_csv('/Users/emg/Programming/GitHub/mod-timelines/tidy-data/{}-mod-hist.csv'.format(sub), index_col=0)
    names = df['name'].unique()
    
    dfs = []
    for name in names:
        n = len(names)
        print(n, name)
        dfs.append(new_layout(name))
        n -= 1
    
    df = pd.concat(dfs)
    df.reset_index(drop=True, inplace=True)
    
    return df

df = run('cmv')