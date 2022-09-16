# -*- coding: utf-8 -*-
"""
Created on Thu Aug  4 14:20:15 2022

@author: braxt
"""

import os
import eyed3
from count_cuss_words import lyrics_search
from download_images import get_album_cover
from concurrent.futures import ThreadPoolExecutor, as_completed


def getLyrics(album_artist, title):
    cover, site, ids = get_album_cover(album_artist, title)
    lyrics = lyrics_search(ids=ids)
    lyrics = lyrics.replace('EmbedShare URLCopyEmbedCopy', '')[:-5]
    # audiofile.lyrics.set(lyrics)
    return lyrics


# os.chdir(r'C:\Users\braxt\OneDrive\Music')
os.chdir(r'D:\Music')
if not os.path.exists('Lyrics'):
    os.mkdir('Lyrics')


def write_lyrics(song):
    tag = eyed3.load(song).tag
    name = tag.title
    try:
        lyrics = tag.lyrics[0].text
    except IndexError:
        try:
            artist = tag.artist
            lyrics = getLyrics(artist, name)
        except Exception:
            return
    if lyrics[-1] == '1':
        lyrics = lyrics[:-1]
    lyrics = lyrics.split('\n')[1:]
    lyrics = '<N>'.join(lyrics)
    lyrics = lyrics.encode('UTF-8')
    with open(f'Lyrics/{name}.txt', 'wb') as f:
        f.write(lyrics)
    return name


with ThreadPoolExecutor() as ex:
    threads = []
    for song in os.listdir():
        if not song.endswith('.mp3'):
            continue
        threads.append(ex.submit(write_lyrics, song))
    for t in as_completed(threads):
        print(t.result())
