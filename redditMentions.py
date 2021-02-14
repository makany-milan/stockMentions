import pandas as pd
import numpy as np
import feedparser as fp
from bs4 import BeautifulSoup
from time import sleep
import re
from datetime import date
import csv


subreddits = [
    'https://www.reddit.com/r/wallstreetbets/new.rss',
    'https://www.reddit.com/r/stocks/new.rss',
    'https://www.reddit.com/r/investing/new.rss',
    'https://www.reddit.com/r/Undervalued/new.rss',
    'https://www.reddit.com/r/RobinHoodPennyStocks/new.rss',
    'https://www.reddit.com/r/pennystocks/new.rss',
    'https://www.reddit.com/r/thetagang/new.rss',
    'https://www.reddit.com/r/options/new.rss',
    'https://www.reddit.com/r/options_trading/new.rss',
    'https://www.reddit.com/r/optionstrading/new.rss',
]

BLACKLIST = [
    'US', 'UK', 'DD', 'CAGR', 'EPS', 'CC', 'CSP', 'IV', 'IPO', 'ETF', 'YTM',
    'ITM', 'ATM', 'OTM', 'CEO', 'COO', 'CIO', 'OPEN', 'ETF', 'EV', 'THE', 'MEME',
    'NOT', 'ALL', 'TLDR', 'IN', 'IMO', 'IMHO', 'USA', 'AND', 'OR', 'NICE', 'NYSE',
    'WTF', 'CNBC', 'HERE', 'FOR', 'FULL', 'TREE', 'MAP', 'CPI', 'MTD', 'WEEK',
    'LINK', 'AS', 'OF', 'YTD', 'QTD', 'WTD', 'EOD', 'EOW', 'DTE', 'MOST', 'TIME',
    'NONE', 'DAY', 'WEEK', 'AM', 'PM', 'NET', 'IF', 'YOY', 'MOM', 'WOW', 'IF',
    'AUS', 'EU', 'OR', 'FAQ', 'BUT', 'YES', 'TAM', 'TIME', 'TO', 'MAKE', 'POST',
    'HEAD', 'FROM', 'TO', 'PC', 'LOL', 'THAT', 'WAS', 'WELL', 'NEW', 'USD', 'EUR',
    'GBP', 'EURO', 'GDP', 'NBA', 'NFL', 'MLB', 'KIDS', 'FOR', 'THE', 'WSB', 'PLAN',
    'EACH', 'GANG', 'LVIE', 'EVER', 'VERY', 'XXX', 'PAPA', 'ELON', 'MUSK', 'GET', 'ON',
    'TRAIN', 'CHO', 'CHOO', 'PAST', 'NEXT', ''
    ]


WHITELIST = []
with open(r'C:\Users\Milan\OneDrive\Desktop\Dad\RedditMentions\data\tickers.csv', 'r') as r:
    reader = csv.reader(r)
    for row in reader:
        ticker = row[0]
        if ticker != 'Symbol':
            WHITELIST.append(ticker)


def getFeed(url: str):
    r = fp.parse(url)
    if r['status'] == 200:
        return r
    else:
        print(r['status'])
        return ''


def getTickers(blob: str):
    tickers = []
    
    soup = BeautifulSoup(blob, 'html.parser')
    try:
        post = soup.text
        t1 = re.findall(r'[$][A-Z][\S]*', str(post))
        t2 = re.findall(r'\b[A-Z]{2,4}\b[.!?]?', str(post))
    except:
        t1 = re.findall(r'[$][A-Z][\S]*', str(blob))
        t2 = re.findall(r'\b[A-Z]{2,4}\b[.!?]?', str(blob))
    
    
    t1 = re.findall(r'[$][A-Z][\S]*', str(blob))
    t2 = re.findall(r'\b[A-Z]{2,4}\b[.!?]?', str(blob))

    if t1 != []:
        for t in t1:
            t = t.replace('.', '').replace(',', '').replace('?', '').replace('!', '').replace('$', '').replace(')', '').replace('(', '')
            if t not in tickers:
                if t in WHITELIST:
                    if t not in BLACKLIST:
                        tickers.append(t)
    if t2 != []:
        for t in t2:
            t = t.replace('.', '').replace(',', '').replace('?', '').replace('!', '').replace(')', '').replace('(', '')
            if t not in tickers:
                if t in WHITELIST:
                    if t not in BLACKLIST:
                        tickers.append(t)

    return tickers
        

def exportLinks(link: str):
    with open(r'C:\Users\Milan\OneDrive\Desktop\Dad\RedditMentions\data\links.txt', 'a') as a:
        a.write(link + '\n')


def importLinks():
    links = []
    with open(r'C:\Users\Milan\OneDrive\Desktop\Dad\RedditMentions\data\links.txt', 'r') as r:
        for line in r:
            links.append(line.strip())
    return links


if __name__ == '__main__':
    read = importLinks()
    df = pd.read_excel(r'C:/Users/Milan/OneDrive/Desktop/Dad/RedditMentions/data/stockData.xlsx', engine='openpyxl')
    # df = pd.DataFrame(columns=['date', 'sub', 'ticker', 'mentions'])
    for item in subreddits:
        r = getFeed(item)
        if r != '':
            for entry in r['entries']:
                if entry['link'] not in read:
                    exportLinks(entry['link'])
                    ts = getTickers(entry['content'][0]['value'])
                    for t in ts:
                        today = date.today()
                        sub = item.split('/')[-2]
                        loc = df.loc[(df['ticker'] == t) & (df['date'] == today) & (df['sub'] == sub)]
                        if loc.empty:
                            df2 = pd.DataFrame({'date': [today], 'sub': [sub], 'ticker': [t], 'mentions': [1]})
                            df = df.append(df2, ignore_index=True)
                        else:
                            df.loc[(df['ticker'] == t) & (df['date'] == today) & (df['sub'] == sub), 'mentions'] += 1
                else:
                    pass

    w = pd.ExcelWriter(r'C:/Users/Milan/OneDrive/Desktop/Dad/RedditMentions/data/stockData.xlsx')
    df.to_excel(w, index=False)
    w.close()
