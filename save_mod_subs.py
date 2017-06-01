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

def get_mod_type(df, name, mode=0):
    current = df['pubdate'].max()
    subset = df[df['name']==name]
    if mode == 0:
        return 0
    if current not in list(subset['pubdate']):
        if '+all' not in list(subset['permissions']):
            return 1
        else:
            return 2
    if current in list(subset['pubdate']):
        if '+all' not in list(subset['permissions']):
            return 3
        else:
            return 4
    else:
        return 'ERROR'

def mod_list(name, sub):
    url = 'https://www.reddit.com/user/{}/moderated_subreddits.json'.format(name)
    r = requests.get(url, {'user-agent':'ThisIsABot'})
    r = requests.get('https://www.reddit.com/user/{}/moderated_subreddits.json'.format(name), headers={'user-agent': 'ThisIsABot'})
    data = r.json()

    path = os.path.join('moding-data', '{}'.format(sub), str(date.today()), '{}.json'.format(name))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    with open(path, 'w') as f:
        json.dump(data, f)

#    path = os.path.join('moding-data', '{}'.format(sub), str(date.today()), '{}'.format(name))
#    os.makedirs(os.path.dirname(path), exist_ok=True)
#    
#    with open(path, 'r') as f:
#        try:
#            data = json.load(f)
#        except:
#            data = {}
    
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
 
def edgelist(sub, df):
    names = df['name'].unique()
    
    dfs = []
    n = len(names)
    for name in names:
        print(n, name)
        dfs.append(mod_list(name, sub))
        n -= 1
    
    edgelist = pd.concat(dfs)
    edgelist.reset_index(drop=True, inplace=True)
    
    edgelist_path = os.path.join('moding-data', '{}'.format(sub), str(date.today()), 'lists', 'edgelist.csv')
    os.makedirs(os.path.dirname(edgelist_path), exist_ok=True)
    edgelist.to_csv(edgelist_path, index=False)

    
    return edgelist


def nodelist(sub, edgelist, df):
    nodelist = pd.DataFrame(list(set(edgelist['mod'])) + list(set(edgelist['sub'])))
    modes = [1]*len(list(set(edgelist['mod']))) + [0]*len(list(set(edgelist['sub'])))
    nodelist['type'] = modes
    nodelist.rename(columns={0 : 'mod'}, inplace=True)
    nodelist['mod_types'] = nodelist.apply(lambda row: get_mod_type(df, row['mod'], row['type']), axis=1)
    
    nodelist_path = os.path.join('moding-data', '{}'.format(sub), str(date.today()), 'lists', 'nodelist.csv')
    os.makedirs(os.path.dirname(nodelist_path), exist_ok=True)
    nodelist.to_csv(nodelist_path, index=False)

    return nodelist

def run(sub):
    #update modtimelines first
    # sub = 'cmv' or 'td
    df_path = os.path.join('tidy-data', '{}-mod-hist.csv'.format(sub))
    df = pd.read_csv(df_path, index_col=0)
    os.makedirs(os.path.dirname(df_path), exist_ok=True)
    print('MAKING {} EDGELIST...'.format(sub))
    e = edgelist(sub, df)
    print('MAKING {} NODELIST...'.format(sub))
    nodelist(sub, e, df)
    
def run_both():
    run('td')
    print('')
    print('')
    run('cmv')

