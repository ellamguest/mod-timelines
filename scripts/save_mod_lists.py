#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  2 13:11:09 2017

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
    
def run():
    update_mod_list('td', 'The_Donald')
    time.sleep(2)
    print('')
    update_mod_list('cmv', 'changemyview')
