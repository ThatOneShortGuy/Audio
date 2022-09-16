import requests
import lxml.html
import sys
from ytmusicapi import YTMusic
import lyricsgenius as lg
import os


def get_lyrics(artist, song):
    more = False
    if isinstance(artist, (tuple, list)):
        more = artist[1:]
        artist = artist[0]
    tempartist = artist.split()
    for i in ['&', ',']:
        if i in tempartist:
            artist = ' '.join(tempartist[:tempartist.index(i)])
    if more:
        artist += '-and-'+more.lower().replace(' ', '-').replace("'", "")
    temptitle = song.split()
    for i in ['(ft.', 'ft.', 'feat.', '(feat.', '(feat', 'feat', 'ft', '(Feat.']:
        if i in temptitle:
            song = ' '.join(temptitle[:temptitle.index(i)])
            break

    artist = artist.lower().replace(' ', '-').replace("'", "").replace('$', '').capitalize()
    song = song.lower().replace(' ', '-').replace('!', '')
    site = f'https://genius.com/{artist}-{song}-lyrics'
    r = requests.get(site)
    if r.ok:
        site = lxml.html.fromstring(r.content)
        lyrics = site.xpath('/html/body/div[1]/main/div[2]/div[3]')[0]
        return '\n'.join(lyrics.itertext())[:-33]


def read_cuss_words(file, delim='\n'):
    return [word for word in open(file).read().split(delim)]


def count_cuss_words(text, term):
    if not isinstance(term, str):
        term = ' '.join(term)
    cuss_words = read_cuss_words(os.path.dirname(os.path.realpath(__file__))+'/cuss_words.txt')
    text = text.lower()
    d = {}
    for word in cuss_words:
        for i in range(len(text)-len(word)):
            check_word = text[i: i + len(word)]
            if check_word == word:
                if word in d:
                    d[word] += 1
                else:
                    d[word] = 1
    d['Total'] = sum(d[word] for word in d)
    d['Words'] = len(text.split())
    d['Cuss %'] = round(d['Total'] / d['Words'] * 100, 2)
    yield d
    try:
        ytmusic = YTMusic()
        search = ytmusic.search(term)
        duration = search[0]['duration']
        mins, secs = duration.split(':')
        duration = int(mins) + int(secs)/60
        d['Words/min'] = round(d['Words']/duration, 2)
    except:
        pass
    yield d


def search(term):
    if not isinstance(term, str):
        term = ' '.join(term)
    print(f'Finding {term}')
    ytmusic = YTMusic()
    term = ytmusic.search(term)
    for i in term:
        if i['resultType'] == 'song':
            artist = i['artists'][0]['name']
            title = i['title']
            print(f'Found "{title}" by "{artist}"')
            return artist, title


def lyrics_search(term=None, ids=None):
    if not isinstance(term, str) and term:
        term = ' '.join(term)
    if term:
        print(f'searching for {term}')
    if not os.path.exists(os.path.dirname(os.path.realpath(__file__))+'/genius_token.txt'):
        token = input('Please input your genius API token (one time): ')
        open(os.path.dirname(os.path.realpath(__file__))+'/genius_token.txt', 'w').write(token)
    genius = lg.Genius(open(os.path.dirname(os.path.realpath(__file__))+'/genius_token.txt').read())
    genius.verbose = False
    if term:
        song = genius.search_song(term, get_full_info=False)
        print(f"Found {song.title} by {song.artist}")
        song = song.lyrics
    else:
        song = genius.lyrics(ids)
    return song


if __name__ == '__main__':
    # sys.argv.append('senpai life')
    if len(sys.argv) > 1:
        if sys.argv[1] == '-s':
            term = sys.argv[2:]
            lyrics = lyrics_search(term)[:-28]
            print(lyrics, end='\n\n')
        else:
            term = sys.argv[1:]
            lyrics = lyrics_search(term)[:-28]
            print('')
        gen = count_cuss_words(lyrics, term)
        for _ in range(2):
            print(f'\r{next(gen)}', end='\r')
    else:
        print(count_cuss_words(get_lyrics('mc virgins', 'anime thighs')))
