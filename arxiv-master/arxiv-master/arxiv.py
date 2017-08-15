#!/usr/bin/env python

import feedparser
import json
import os
import re
import sys
import tarfile
import time
import tweepy
import urllib
import wand.image

settings = {}
articles = []

def update_settings():
    global settings
    id = settings.get('id', '')
    with open('arxiv.json') as file:
        settings = json.load(file)
    if id: settings['id'] = id
    with open('arxiv.json', 'w') as file:
        json.dump(settings, file, indent=4)

def update_feed(feed):
    def compare(x, y):
        return x + [y] if x[-1] != y else x
    global articles
    url = 'http://arxiv.org/rss/' + feed
    info = 'Updating {}\t'.format(feed)
    sys.stdout.write(info)
    sys.stdout.flush()
    count = 0
    for x in feedparser.parse(url).entries:
        m = re.search('(.*) \(arXiv:(.*)v(.*) \[.*\]\)', x.title)
        if m and m.group(1) and m.group(2) and int(m.group(3)) == 1:
            articles.append({'id': m.group(2), 'title': m.group(1)})
            count += 1
    cursor = settings.get('id', '')
    sys.stdout.write('{}\n'.format(count))
    articles = sorted(articles, key=lambda x: x['id'])
    articles = reduce(compare, articles, [{'id': 0}])
    articles = filter(lambda x: x['id'] > cursor, articles)
    articles = articles[:48]

def update_all_feeds():
    global articles
    articles = []
    for feed in settings.get('feeds', []):
        update_feed(feed)
        time.sleep(5)

def cleanup_article(article):
    id = article['id']
    try :
        for root, dirs, files in os.walk(id, False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.remove(id + '.tar.gz')
        os.rmdir(id)
    except:
        pass

def download_article(article):
    def progress(count, block, size):
        percent = min(int(100 * count * block / size), 100)
        info = '\rDownloading {}\t{}%'.format(id, percent)
        sys.stdout.write(info)
        sys.stdout.flush()
    id = article['id']
    cleanup_article(article)
    url = 'http://arxiv.org/e-print/'
    urllib.urlretrieve(url + id, id + '.tar.gz', progress)
    sys.stdout.write('\n')
    os.mkdir(id)
    with tarfile.open(id + '.tar.gz') as tar:
        tar.extractall(id)

def convert_images(article):
    for root, dirs, files in os.walk(article['id'], False):
        for file in files:
            name, ext = os.path.splitext(os.path.join(root, file))
            if ext in {'.pdf', '.eps'}:
                page = name + ext + '[0]'
                info = 'Converting {}\n'.format(name + ext)
                sys.stdout.write(info)
                try:
                    with wand.image.Image(filename = page) as img:
                        img.save(filename = name + '.png')
                except:
                    pass

def get_images(article):
    images = []
    convert_images(article)
    for root, dirs, files in os.walk(article['id'], False):
        for file in files:
            name, ext = os.path.splitext(os.path.join(root, file))
            if ext in {'.png', '.jpg'}:
                images.append(name + ext)
    images.sort(key = lambda x: -os.stat(x).st_size)
    return [images[0], images[1], images[2], images[3]]

def get_token():
    auth = tweepy.OAuthHandler(
        settings['oauth']['consumer_key'],
        settings['oauth']['consumer_secret'])
    auth.set_access_token(
        settings['oauth']['access_token'],
        settings['oauth']['access_token_secret'])
    return tweepy.API(auth)

def tweet_article(api, article):
    download_article(article)
    message = '{title} arxiv.org/abs/{id}'
    count = len(message.format(**article)) + 23
    if count > 140:
        article['title'] = article['title'][:140 - count - 3].strip() + '...'
    media = [api.media_upload(i).media_id_string for i in get_images(article)]
    header = message.format(**article)
    api.update_status(status=header, media_ids=media)
    settings['id'] = article['id']
    update_settings()
    date = time.strftime('%a, %d %b %Y %H:%M:%S')
    info = '{} \033[01;35m{}\033[0;0m\n'.format(date, message)
    sys.stdout.write(info.format(**article))

update_settings()
api = get_token()

while True:
    update_all_feeds()
    while len(articles) > 0:
        article = articles[0]
        articles = articles[1:]
        try:
            tweet_article(api, article)
        except:
            time.sleep(5)
            continue
        finally:
            cleanup_article(article)
        timeout = int(settings.get('timeout', 60)) * 60
        time.sleep(timeout)
    else:
        time.sleep(600)
