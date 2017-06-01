#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  2 14:23:59 2017

@author: emg
"""
import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import date
import pickle
import os
import logging
import logging.handlers

LOGGING_DIR = 'logging/logs.txt'


### GETTING REDDIT API CREDENTIALS
with open('credentials.json', 'r') as f:
     data = json.load(f)

headers={'User-agent':data['user_agent']}

### CREATE EDGELIST + NODELIST FUNCTIONS
def make_soup(url):
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    return soup

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

def get_lists(df):
    ''' return edgelist, nodelist from df with
        colums (moderator) 'name' and 'sub'
    '''
    names = list(set((df[df['name']!='AutoModerator']['name'])))

    print('Pulling moderated sub lists...')
    logging.info('Pulling moderated sub lists...')
    d = {}
    errors = [] # errors are mods for whom mod sub lists were not retrieved
    n = len(names)
    for name in names:
        print(n, name)
        n -= 1
        url = 'https://www.reddit.com/user/{}'.format(name)
        soup = make_soup(url)
        try:
            table = soup.find('ul', {'id':'side-mod-list'})
            items = table.find_all('li')
            subs = []
            for item in items:
                subs.append(item.a['title'])
            d[name] = subs
        except:
            errors.append(name)
            print('ERROR')
            pass
        time.sleep(1)
    print('moderated subreddit list not captured for', len(errors), 'moderators')
          
    edgelist = [] 
    for key in d.keys():
        for value in d[key]:
            edgelist.append([key, value])
    
    edgelist = pd.DataFrame(edgelist)
    edgelist.columns = ['mod', 'sub']
    
    nodelist = pd.DataFrame(list(set(edgelist['mod'])) + list(set(edgelist['sub'])))
    modes = [1]*len(list(set(edgelist['mod']))) + [0]*len(list(set(edgelist['sub'])))
    nodelist['type'] = modes
    nodelist.rename(columns={0 : 'mod'}, inplace=True)
    nodelist['mod_types'] = nodelist.apply(lambda row: get_mod_type(df, row['mod'], row['type']), axis=1)
    
    mod_types = []
    
    current = df['pubdate'].max()
    subset = df[df['name']==name]
    for name in edgelist['mod']:
        print(name)
        mode = nodelist[nodelist['mod']==name]
        if mode == 0:
            print(0)
        if current not in list(subset['pubdate']):
            if '+all' not in list(subset['permissions']):
                print(1)
            else:
                print(2)
        if current in list(subset['pubdate']):
            if '+all' not in list(subset['permissions']):
                print(3)
            else:
                print(4)
        else:
            print('ERROR')
        

def save_lists(sub):
    logging.info('Running for {}...'.format(sub))
    '''sub = 'td' or 'cmv'''
    df_path = os.path.join('data', '{}'.format(sub), 'mod-hist')
    os.makedirs(os.path.dirname(df_path), exist_ok=True)
    
    logging.info('opening mod hist')
    df = pd.read_csv(df_path, index_col=0)
    logging.info('Getting lists...')
    df = df.head(n=20)
    errors, edgelist, nodelist = get_lists(df)
    
    logging.info('storing errors')
    error_path = os.path.join('data', sub, 'errors', str(date.today()))
    os.makedirs(os.path.dirname(error_path), exist_ok=True)
    with open(error_path, 'wb') as fp:
        pickle.dump(errors,fp)
    
    logging.info('storing edgelist ')
    edgelist_path = os.path.join('data', sub, 'edgelists', str(date.today()))
    os.makedirs(os.path.dirname(edgelist_path), exist_ok=True)
    edgelist.to_csv(edgelist_path, index=False)

    logging.info('storing nodelist')
    nodelist_path = os.path.join('data', sub, 'nodelists', str(date.today()))
    os.makedirs(os.path.dirname(nodelist_path), exist_ok=True)
    nodelist.to_csv(nodelist_path, index=False)
    
    logging.info('Finished for {}'.format(sub))



### UPDATE DATA
def run():
    save_lists('cmv')
    save_lists('td')
    
def _configure_logging():
    os.makedirs(os.path.dirname(LOGGING_DIR), exist_ok=True)
    file_handler = logging.handlers.TimedRotatingFileHandler(LOGGING_DIR, 
                                                             when='W0', 
                                                             backupCount=7)
    
    logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[logging.StreamHandler(),
                              file_handler])

run()    
_configure_logging()
