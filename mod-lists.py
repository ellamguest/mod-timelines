#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  2 16:54:56 2017

@author: emg
"""
import pandas as pd
import json
from datetime import date
import os

def get_mod_type(df, name, mode=0):
    current = df['pubdate'].max()
    subset = df[df['name']==name]
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

def list_to_df(name, sub):
    '''loads json of today's mod list for sub
    must have run save_mod_subs first
    converts to df
    '''
    path = os.path.join('moding-data', '{}'.format(sub), str(date.today()), '{}.json'.format(name))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    with open(path, 'r') as f:
        try:
            data = json.load(f)
        except:
            data = {}
    
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
    df['name'] = name
    df['date'] = date.today()
      
    return df
 
def make_edgelist(sub, df):
    names = list(df['name'].unique())
    names.remove('AutoModerator')
    
    dfs = []
    n = len(names)
    print ('Getting current moderating subs list for {} moderators'.format(sub))
    print()
    for name in names:
        print(n, name)
        dfs.append(list_to_df(name, sub))
        n -= 1
    
    print('MAKING {} EDGELIST...'.format(sub))
    edgelist = pd.concat(dfs)
    edgelist.reset_index(drop=True, inplace=True)
    edgelist['sub'] = 'r/' + edgelist['sub'].astype('str')
    edgelist = edgelist[['name','sub','subscribers','date']]
    
    edgelist_path = os.path.join('moding-data', sub, str(date.today()), 'lists', 'edgelist.csv')
    os.makedirs(os.path.dirname(edgelist_path), exist_ok=True)
    edgelist.to_csv(edgelist_path, index=False)

    return edgelist


def make_nodelist(sub, edgelist, df):
    
    print('MAKING {} NODELIST...'.format(sub))
    d = {}
    d['name'] = list(set(edgelist['name'])) + list(set(edgelist['sub']))
    d['type'] = [1]*len(list(set(edgelist['name']))) + [0]*len(list(set(edgelist['sub'])))
    nodelist = pd.DataFrame.from_dict(d, orient='columns')
    nodelist['mod_type'] = nodelist.apply(lambda row: get_mod_type(df, row['name'], row['type']), axis=1)
    
    nodelist_path = os.path.join('moding-data', sub, str(date.today()), 'lists', 'nodelist.csv')
    os.makedirs(os.path.dirname(nodelist_path), exist_ok=True)
    nodelist.to_csv(nodelist_path, index=False)
    

def run(sub):
    #update modtimelines first
    # sub = 'cmv' or 'td
    df_path = os.path.join('mod-list-data', '{}'.format(sub), 'master.csv')
    df = pd.read_csv(df_path)
    print(), print()
    
    print()
    e = make_edgelist(sub, df)
    
    print()
    make_nodelist(sub, e, df)
    
def run_both():
    run('td')
    print()
    print()
    run('cmv')