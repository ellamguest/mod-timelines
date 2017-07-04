import pandas as pd
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np

### FUCNTIONS TO CONVERT MOD INSTANCES DF TO MOD PRESENCE TIMELINE
def prep_df(df):
    '''subset df into required columns and types
    to construct timeline df'''
    df['date'] = pd.to_datetime(df['date']).dt.normalize()
    df['pubdate'] = pd.to_datetime(df['pubdate']).dt.normalize()
    df.sort_values('pubdate', inplace=True)
    df['perm_level'] = df['permissions'].map({'+all':2}).fillna(1)
    last = df['pubdate'].max()
    n = {1:3,2:4, 0:0} 
    current = list(df[df['pubdate']==last]['name'])
    df.reset_index(inplace=True)
    c = df[df['name'].isin(current)]['perm_level'].map(n)      
    df.perm_level.update(c)     
    df.sort_values(['date','pubdate'], inplace=True)
    df.drop_duplicates(['name','date'], keep='last', inplace=True)
    df.set_index('name', inplace=True, drop=False)
    df = df[['name','date','pubdate','perm_level']]
    return df

def date_presence_dict(dates, start, end, perm_level): 
    '''check mod presence on date'''
    d = {}
    for date in dates:
        if date >= start and date <= end:
            d[date] = perm_level
    return d

def timeline_df(df):
    '''convert moderator instance date to timeline df'''
    df = prep_df(df)
    timeline = pd.DataFrame(index = pd.date_range(start = df['date'].min(),
                                                  end = df['pubdate'].max(),
                                                  freq='D'))
    for name in set(df['name']):
        if list(df['name']).count(name) == 1:
            subset = df.loc[name]
            dates = pd.date_range(start = subset['date'],
                                  end = subset['pubdate'],
                                  freq='D')
            start, end, perm_level = subset['date'], subset['pubdate'], subset['perm_level']
            d = date_presence_dict(dates, start, end, perm_level)
            timeline[name] = pd.Series(d)

        elif list(df['name']).count(name) > 1:
            combined = {}
            subset = df.loc[name]
            dates = pd.date_range(start = subset['date'].min(),
                                  end = subset['pubdate'].max(),
                                   freq='D')
            for row in subset.itertuples():
                start, end, perm_level = row[2], row[3], row[4]
                d = date_presence_dict(dates, start, end, perm_level)
                combined.update(d)
            timeline[name] = pd.Series(combined)
    timeline.fillna(0, inplace=True)
    timeline = timeline[list(df.sort_values(['date','pubdate'])['name'].drop_duplicates())]
    return timeline




####### PLOTTING FUNCTIONS
def set_cmap():
    colours = ['white','royalblue','midnightblue','indianred','maroon']
    cmap = LinearSegmentedColormap.from_list('Custom', colours, len(colours))
    return cmap

def td_data():
    '''open td moderator instance df'''
    df = pd.read_csv('/Users/emg/Programming/GitHub/mod-timelines/tidy-data/td-mod-hist.csv', index_col=0)
    return prep_df(df)

def td_plot():
    td_df = pd.read_csv('/Users/emg/Programming/GitHub/mod-timelines/tidy-data/td-mod-hist.csv', index_col=0)
#    td_df = pd.read_csv('/Users/emg/Programming/GitHub/mod-timelines/mod-list-data/td/history.csv', index_col=0)
    td_timeline = timeline_df(td_df)
    
     
    fig = plt.figure(figsize=(15,9.27))
    ax = sns.heatmap(td_timeline, cmap=set_cmap())
   
    start, end = ax.get_ylim()
    ax.set_yticks(np.arange(start, end, 60))
    ax.set_yticklabels(list(td_timeline.index.strftime('%Y-%m')[::-60]))
    #plt.tick_params(axis='x',which='both', labelbottom='off')
    plt.tick_params(axis='x',which='both', labelsize=6)
    
    plt.title('r/The_Donald Moderator Presence Timeline')
    plt.xlabel('r/The_Donald Moderators', labelpad=20)
    plt.ylabel('Moderator Presence by Date', labelpad=10)
    
    colorbar = ax.collections[0].colorbar
    colorbar.set_ticks([1.2, 2.0, 2.8, 3.6])
    colorbar.set_ticklabels(['Former non-top',
                             'Former top',
                             'Current non-top',
                             'Current top'])
    
    # adding event reference lines
    days = list(td_timeline.index)
    days.reverse()
    plt.axhline(y=days.index(datetime(2016,11,8,0,0,0)), ls = 'dashed', color='black', label='Election')
    plt.axhline(y=days.index(datetime(2016,11,24,0,0,0)), ls = 'dotted', color='green', label='Spezgiving')
    plt.axhline(y=days.index(datetime(2017,1,21,0,0,0)), ls = 'dotted', color='black', label='Inauguration')
    plt.axhline(y=days.index(datetime(2017,5,2,0,0,0)), ls = 'dashed', color='green', label='Demodding')
    
    plt.legend(loc=9)
    
    plt.tight_layout()
    plt.savefig('/Users/emg/Programming/GitHub/mod-timelines/figures/td-mod-timeline.png', dpi=fig.dpi)

def cmv_plot():
#    cmv_df = pd.read_csv('/Users/emg/Programming/GitHub/mod-timelines/tidy-data/cmv-mod-hist.csv', index_col=0)
    cmv_df = pd.read_csv('/Users/emg/Programming/GitHub/mod-timelines/mod-list-data/cmv/history.csv', index_col=0)
    cmv_timeline = timeline_df(cmv_df)
    
    fig = plt.figure(figsize=(8.5, 12.135))
    ax = sns.heatmap(cmv_timeline, cmap=set_cmap())
    start, end = ax.get_ylim()
    ax.set_yticks(np.arange(start, end, 120))
    ax.set_yticklabels(list(cmv_timeline.index.strftime('%Y-%m')[::-120]))
    #plt.tick_params(axis='x',which='both', labelbottom='off')
    
    plt.title('CMV Moderator Presence Timeline', y=1.03, x=0.4, fontweight='bold')
    plt.xlabel('r/ChangeMyView Moderators',  labelpad=20)
    plt.ylabel('Moderator Presence by Date',  labelpad=10)
    
    colorbar = ax.collections[0].colorbar
    colorbar.set_ticks([1.2, 2.0, 2.8, 3.6])
    colorbar.set_ticklabels(['Former non-top',
                             'Former top',
                             'Current non-top',
                             'Current top'])
    
    plt.tight_layout()
    plt.savefig('/Users/emg/Programming/GitHub/mod-timelines/figures/cmv-mod-timeline.png', dpi=fig.dpi)



