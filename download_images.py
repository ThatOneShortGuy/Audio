# -*- coding: utf-8 -*-
"""
Created on Tue May 18 13:26:33 2021

@author: braxt
"""

import requests
import shutil
import os
import lyricsgenius as lg


def get_album_cover(artist, title, album=None):
    term = title + ' ' + artist
    album = album or title
    print(f'searching for {term}')
    if not os.path.exists(os.path.dirname(os.path.realpath(__file__))+'/genius_token.txt'):
        token = input('Please input your genius API token (one time): ')
        open(os.path.dirname(os.path.realpath(__file__))+'/genius_token.txt', 'w').write(token)
    genius = lg.Genius(open('genius_token.txt').read())
    genius.verbose = False
    song = genius.search_song(term, get_full_info=False)
    url = song.song_art_image_url
    site = song.url
    ids = song.api_path.split('/')[-1]
    if not os.path.exists('images'):
        os.mkdir('images')
    if os.path.exists(path := f'images/{album}.jpg'):
        return path, site, ids
    elif os.path.exists(path := f'images/{album}.png'):
        return path, site, ids
    path = 'images/'+str(album)+url[-4:]
    if url != 'https://assets.genius.com/images/winking_sgnarly.gif?1623773784':
        download(url, path)
        return path, site, ids
    return False, site, ids


def download(url, name):
    name = str(name)
    r = requests.get(url, stream=True)
    if r.ok:
        with open(name, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)


if __name__ == '__main__':
    artist = "Shiki-TMNS"
    title = 'Anime Bitch'
    get_album_cover(artist, title)
