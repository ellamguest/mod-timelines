# -*- coding: utf-8 -*-
"""
Created on Fri Dec  2 16:47:04 2016

@author: emg
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import glob
import re

### GENERAL FUNCTIONS

def make_soup(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup

### AIS SCRAPING + COMPILING FUNCTIONS
def get_ais_snapshots():
    source = 'https://archive.is/https://www.reddit.com/r/The_Donald/about/moderators'
    r = requests.get(source)
    soup = BeautifulSoup(r.text, "html.parser")
    snaps = soup.findAll('img', {'alt':"screenshot of https://www.reddit.com/r/The_Donald/about/moderators"})
    
    urls = []
    for snap in snaps:
        url = snap.parent['href']
        urls.append(url)
    return urls  

def save_snapshots(urls):
    #save wbm td snapshot at time to file
    filenames = glob.glob("/Users/emg/Google Drive/PhD/data/the_donald/td-is-snapshots/td-is-*.html")
    old_ids = [fn.strip('https://archive.is/').strip('.html') for fn in filenames]
    for url in urls:
        url_id = url.strip('https://archive.is/')
        if url_id not in old_ids:
            response = requests.get(url)
            filename = "/Users/emg/Google Drive/PhD/data/the_donald/td-is-snapshots/td-is-{}.html".format(url_id)
            with open(filename, "wb") as file:
                file.write(response.content)


def load_ais_snapshot(html):
    f = open(html, 'r')
    return f.read() 

def ais_snapshot_df(html):
    soup = BeautifulSoup(html, 'html.parser')
    mods = soup.findAll('input', {'value':'moderator'})
    
    d = {}
    for mod in mods:
        name = mod.parent.findAll('input', {'name':'name'})[0]['value']
        date = mod.parent.parent.parent.parent.time['title']
        permissions = mod.parent.findAll('input', {'name':'permissions'})[0]['value']
        karma = mod.parent.parent.parent.parent.b.text
        d[name] = [date, permissions, karma]  
    
    df = pd.DataFrame.from_dict(d, orient="index")
    df['pubdate'] = soup.findAll('time')[0].text
    return df 

def compile_ais_snapshots():
    dfs = []
    htmls = glob.glob("/Users/emg/Google Drive/PhD/data/the_donald/td-is-snapshots/td-is-*.html")
    for html in htmls:
        html = load_ais_snapshot(html)
        dfs.append(ais_snapshot_df(html))
    
    df = pd.concat(dfs)
    df.reset_index(inplace=True)
    df.columns = ['name', 'date','permissions','karma','pubdate']   
    df['date'] = pd.to_datetime(df['date'])
    df['pubdate'] = pd.to_datetime(df['pubdate'])
    return df


### WBM SCRAPING + COMPILING FUNCTIONS

def get_wbm_times():
    cdx = 'http://web.archive.org/cdx/search/cdx?url=https://www.reddit.com/r/The_Donald/about/moderators'
    response = requests.get(cdx)
    text = response.text
    lines = text.splitlines()
    
    times = []
    for line in lines:
        time = line.split(' ')[1]
        times.append(time)
    return times
    
def save_snapshot(time):
    #save wbm td snapshot at time to file
    url = 'http://web.archive.org/web/{}/https://www.reddit.com/r/The_Donald/about/moderators'.format(time)
    response = requests.get(url)
    
    filename = "/Users/emg/Google Drive/PhD/data/the_donald/td-wbm-snapshots/td-wbm-{}.html".format(time)
    with open(filename, "wb") as file:
        file.write(response.content)

def load_wbm_snapshot(time):
    f = open("/Users/emg/Google Drive/PhD/data/the_donald/td-wbm-snapshots/td-wbm-{}.html".format(time), 'r')
    return f.read() 
    
def snapshot_df(time):
    html = load_wbm_snapshot(time)
    soup = BeautifulSoup(html, 'html.parser')
    try:
        table = soup.findAll("div", {"class":"moderator-table"})[0]
    except IndexError:
        pass
    else:
        rows = table.find_all('tr')           
        
        d = {}
        for row in rows:          
            name_karma = row.findAll('span', {'class':'user'})[0].text
            name = name_karma.split(u'\xa0')[0]
            karma = name_karma.split(u'\xa0')[1]
            date = row.findAll('time')[0]['datetime']
            permissions = row.findAll('input', {'name':'permissions'})[0]['value']
            d[name] = [date, permissions, karma]   
        d.keys()
        
        df = pd.DataFrame.from_dict(d, orient="index")
        df['pubdate'] = time
        return df

def compile_dfs(times):   
    dfs = []
    errors = []
    for time in times:
        df = snapshot_df(time)
        if isinstance(df, pd.DataFrame):
            dfs.append(df)
        else:
           errors.append(time)
    df = pd.concat(dfs)
    df.reset_index(inplace=True)
    df.columns = ['name', 'date','permissions','karma','pubdate']
    df['date'] = pd.to_datetime(df['date'])
    df['pubdate'] = pd.to_datetime(df['pubdate'].astype(str), format='%Y%m%d%H%M%S')
    df['karma'] = df['karma'].map(lambda x: x[1:-1])
    return df

def update_snapshots(times):
    filenames = glob.glob("/Users/emg/Google Drive/PhD/data/the_donald/td-wbm-snapshots/td-wbm-*.html")
    old_times = [re.findall(r'\d+', fn)[0] for fn in filenames]
    for time in times:
        if time not in old_times:
            save_snapshot(time)


### RUN
def run_td_ais():
    save_snapshots(get_ais_snapshots())
    print('Saved ais snapshots - compiling mod df now...')
    df = compile_ais_snapshots()
    print('Compiled ais mod df, saving now...')
    df.to_csv('/Users/emg/Programming/GitHub/mod-timelines/raw-data/td/ais-mod-df.csv')

# wbm
def run_td_wbm():
    times = get_wbm_times()
    print('Got wbm times')
    update_snapshots(times)
    print('Updated snapshots - compiling mod df')
    df = compile_dfs(times)
    print('Compiled wbm mod df, saving now...')
    df.to_csv('/Users/emg/Programming/GitHub/mod-timelines/raw-data/td/wbm-mod-df.csv')


def update_td_mod_timeline():
    run_td_ais()
    run_td_wbm()
    
    td_ais = pd.read_csv('/Users/emg/Programming/GitHub/mod-timelines/raw-data/td/ais-mod-df.csv', index_col=0)
    td_wbm = pd.read_csv('/Users/emg/Programming/GitHub/mod-timelines/raw-data/td/wbm-mod-df.csv', index_col=0)
    
    print('Compiling ais and wbm dfs...')
    df = pd.concat([td_ais,td_wbm])
    df.sort_values(['date', 'pubdate'], inplace=True)
    df.reset_index(drop=True, inplace=True)

    print('Saving master td mod timeline...')
    df.to_csv('/Users/emg/Programming/GitHub/mod-timelines/tidy-data/td-mod-hist.csv')
    df.to_csv('/Users/emg/Programming/GitHub/mod-timelines/mod-list-data/td/master.csv')

update_td_mod_timeline()
