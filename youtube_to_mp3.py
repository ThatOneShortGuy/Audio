"""
Created on Tue Mar 30 16:01:42 2021

@author: braxt
"""

import os
import sys
from threading import Thread
import requests
import traceback

from volume_equalizer import equalize, to_ex

import pytube as pt
from ytmusicapi import YTMusic
try:
    import lyricsgenius as lg
    genius_installed = True
except:
    print('Failed to import lyricsgenius, metadata will not be added to songs.')
    genius_installed = False

SELF_FILE = __file__

DEBUG = bool(sys.gettrace())

os.system("")


def prYellow(
    skk, **kwargs): print("\033[93m {}\033[00m" .format(skk), **kwargs)


def prRed(skk, **kwargs): print("\033[91m {}\033[00m" .format(skk), **kwargs)


def prGreen(skk, **kwargs): print("\033[92m {}\033[00m" .format(skk), **kwargs)


def remove_to(inp_text, removal):
    for i in range(len(inp_text)-len(removal)):
        if inp_text[i:i+len(removal)] == removal:
            return inp_text[i:]


def replace(string, li, wit):
    '''Replaces all instances in an iterable li with a string wit in a string.'''
    for i in li:
        string = string.replace(i, wit)
    return string


def video_to_mp3(file_name, equal=False, artist=None, title=None, cover_art=None):
    """ Transforms video file into a MP3 file """
    try:
        file, extension = os.path.splitext(file_name)
        filedir = os.path.dirname(file)
        filedir = os.path.join(filedir, title) if title else file
        if isinstance(artist, str):
            album_artist = artist
        if isinstance(artist, (list, tuple)):
            album_artist = artist[1]
            artist = artist[0]
        # Convert video into .wav file
        err = os.system(
            f'ffmpeg -loglevel quiet -y -i "{file_name}" \
{f"""-metadata artist="{artist}" -metadata album_artist="{album_artist}" """ if artist else ""} \
{f"""-metadata title="{title}" """ if title else ""} -q:a 2 -id3v2_version 3 -vn "{filedir}.wav"')
        if err:
            prRed('ffmpeg failed! unknown error, exiting...')
            sys.exit(err)
        os.remove(file_name)
        if equal:
            try:
                file_name = equalize(
                    filedir+'.wav', (artist, album_artist), title)
            except:
                prYellow(
                    'Failed to equalize volume. Likely librosa or soundfile is not installed. Continuing...')
        file_name = to_ex(file_name, '.mp3', (artist, album_artist), title)
        prGreen(f'{title} Successfully converted to MP3!')
        if cover_art and genius_installed:
            try:
                import eyed3
                import eyed3.id3
            except ImportError:
                raise Exception(
                    """do "pip install eyed3" to install module or don't use cover art.""")

            from download_images import get_album_cover
            try:
                cover, _, ids = get_album_cover(album_artist, title)
                audiofile = eyed3.load(file_name)
                if not os.path.exists(os.path.dirname(os.path.realpath(SELF_FILE))+'/genius_token.txt'):
                    token = input(
                        'Please input your genius API token (one time): ')
                    open(os.path.dirname(os.path.realpath(SELF_FILE)) +
                         '/genius_token.txt', 'w').write(token)
                genius = lg.Genius(open('genius_token.txt').read())
                song = genius.song(ids)['song']
                try:
                    album = song['album']['name']
                    albumId = song['album']['id']
                    trackNum = genius.album_tracks(albumId)["tracks"]
                    for track in trackNum:
                        number = track['number']
                        if track['song']['id'] == int(ids):
                            trackNum = number
                            break
                    audiofile.tag.track_num = trackNum
                    audiofile.tag.album = album
                except:
                    prYellow(f'Failed to add album data for {title}')
                try:
                    audiofile.tag.release_date = song['release_date'][:4]
                except:
                    prYellow(f'Failed to add release date for {title}')
                try:
                    from count_cuss_words import lyrics_search
                    lyrics = lyrics_search(ids=ids)
                    lyrics = lyrics.replace(
                        'EmbedShare URLCopyEmbedCopy', '')[:-5]
                    audiofile.tag.lyrics.set(lyrics)
                except Exception:
                    prYellow(f'Failed to add lyrics for {title}')
                if cover:
                    audiofile.tag.images.set(
                        3, open(f'{cover}', 'rb').read(), f'image/{cover[-3:]}')
                else:
                    prYellow(f'Could not retrieve cover art for {title}')
                audiofile.tag.save()  # version=eyed3.id3.ID3_V2_3)
            except Exception as e:
                print(f'Failed to add add metadata for {title} due to: {e}')
                traceback.print_exc()
        return file+'.mp3'
    except OSError as err:
        prRed(err)
        sys.exit(1)


def youtube_to_mp3(video_link, file_name='D:/Sounds', equalize=True, cover_art=True):
    """Retreives YouTube audio and converts to mp3."""
    a = pt.YouTube(video_link)
    aud = None
    trys = 0
    while not aud:
        try:
            aud = a.streams.filter(only_audio=True)
        except KeyboardInterrupt:
            print('\nExiting...')
            exit()
        except Exception as e:
            print(f'Failed, trying again due to: {e}')
            trys += 1
        if trys > 2:
            aud = a.streaming_data['adaptiveFormats'][-1]['url']
    ma = 0
    maN = 0
    if not isinstance(aud, str):
        for i, e in enumerate(aud):
            if e.itag == 251:
                maN = i
                break
            if (t := int(e.abr.rstrip('kbps'))) > ma:
                ma = t
                maN = i
    try:
        title = a.metadata.metadata[0]['Song']
        artist = a.metadata.metadata[0]['Artist']
        artist, title = artist.split(
            ',')[0], title + ' ft. '+artist.split(',')[1]
    except Exception:
        title = a.title.split(' - ')
        if len(title) == 1:
            title = title[0].split(' – ')
        try:
            artist, title = title[:2]
            artist = artist.strip()
        except Exception:
            artist = a.author
            if artist[0] == '\u200b':
                artist = artist[1:]
            title = title[0]
            if artist == 'Various Artists - Topic':
                artist = a.description.split('\n\n')[1].split('·')[
                    1].replace(' x ', ' & ')
        artist = artist.replace(
            ' - Topic', '').replace('#TeamImouto', '').strip()
    words = open(r'C:\Users\braxt\OneDrive\Documents\Python\Audio\removals.txt',
                 'r').read().split('\n')
    title = replace(title, words, '').replace('  ', ' ').strip()
    artist = artist.replace(' x ', ' & ').replace(' X ', ' & ')
    temptitle = title.split()
    for i in ['(prod.', '(Prod.', '(Directed', '(Dir.', 'prod.', '~Prod']:
        if i in temptitle:
            title = ' '.join(temptitle[:temptitle.index(i)])
            break
    temptitle = title.split()
    featuring = ''
    for i in ['(ft.', 'ft.', 'feat.', '(feat.', '(feat', 'feat', 'ft', '(Feat.', 'w/', 'FT.', '(Ft.']:
        if i in temptitle:
            featuring = ' '.join(temptitle[temptitle.index(i)+1:])
            title = ' '.join(temptitle[:temptitle.index(i)])
            if i[0] == '(':
                featuring = featuring[:-1]
            break
    if featuring:
        artist = (artist + ' feat. ' + featuring, artist)

    try:
        tempartist = artist.split()
        if '&' in tempartist:
            album_artist = ' '.join(tempartist[:tempartist.index('&')])
            artist = (artist, album_artist)
    except AttributeError:
        pass
    print(
        f'Downloading {title} by {artist if isinstance(artist, str) else artist[0]}')
    aud = download(aud, file_name, title, 'mp3', maN)
    print(
        f'Downloaded {title} by {artist if isinstance(artist, str) else artist[0]}')
    return video_to_mp3(aud, equalize, artist, title, cover_art)


def download(file, destination, file_name, ext, maN=None, size=None):
    if isinstance(file, str):
        data = requests.get(file, stream=True)
        with open(f'{destination}/{file_name}.{ext}', 'wb') as f:
            try:
                from progressbar import ProgressBar as bar
            except ImportError:
                try:
                    from tqdm import tqdm as bar
                except ImportError:
                    bar = None
            try:
                if bar:
                    for i, d in enumerate(bar(data.iter_content(2**16))):
                        f.write(d)
                        print(f'{round(((i*2**16)/size)*100,2)}%', end=' ')
                else:
                    for i, d in enumerate(data.iter_content(2**16)):
                        f.write(data)
                        print(f'{round(((i*2**16)/size)*100,2)}%', end='\r')
            except Exception as e:
                prRed(e)
        aud = f'{destination}/{file_name}.{ext}'
    else:
        aud = file[maN].download(f'{destination}')
    return aud


def download_video(video_link, destination=None, vformat=None):
    if isinstance(destination, type(None)):
        destination = os.getcwd()
    a = pt.YouTube(video_link)
    aud = None
    vid = 0
    aud = a.streaming_data['adaptiveFormats'][-1]['url']
    aud_size = a.streaming_data['adaptiveFormats'][-1]['contentLength']
    if vformat:
        vformat = vformat.lower()
        if vformat == 'av1':
            vformat = 'av01'
        elif vformat == 'h264' or vformat == 'h.264' or vformat == '264' or vformat == 'mpeg-4':
            vformat = 'avc1'
        for i in a.streaming_data['adaptiveFormats']:
            if i['mimeType'].split('"')[1].split('.')[0] == vformat:
                vid = i['url']
                vid_type = i['mimeType'].split(';')[0].split('/')[1]
                vid_size = i['contentLength']
                break
        else:
            prRed(f'Could not locate any videos of type {vformat}')
            sys.exit(1)
    else:
        for i in range(3):
            test = a.streaming_data['adaptiveFormats'][i]['mimeType'].split('"')[
                1].split('.')[0]
            vid_size = int(
                a.streaming_data['adaptiveFormats'][i]['contentLength'])/(2**20)
            print(f'{i} - {test}: {round(vid_size, 2)} MB')
        vid = int(input('Which one do you want? '))
        if not vid+1:
            for i in reversed(range(3)):
                test = a.streaming_data['adaptiveFormats'][i]['mimeType'].split('"')[
                    1].split('.')[0]
                if test == 'av01':
                    vid = a.streaming_data['adaptiveFormats'][i]['url']
                    vid_type = a.streaming_data['adaptiveFormats'][i]['mimeType'].split(';')[
                        0].split('/')[1]
                    vid_size = a.streaming_data['adaptiveFormats'][i]['contentLength']
                    break
                if test == 'avc1' and not vid:
                    vid = i
                elif test == 'vp9':
                    vid = i
        if isinstance(vid, int):
            vid_type = a.streaming_data['adaptiveFormats'][vid]['mimeType'].split(';')[
                0].split('/')[1]
            vid_size = a.streaming_data['adaptiveFormats'][vid]['contentLength']
            vid = a.streaming_data['adaptiveFormats'][vid]['url']
    vid_size, aud_size = int(vid_size), int(aud_size)
    print(f'Total Size: {round(vid_size/2**20, 2)} MB video + {round(aud_size/2**20, 2)} MB Audio = {round((aud_size + vid_size)/2**20,2)} MB')

    maN = 0
    file_name = a.title.replace('|', '').replace('"', '')
    aud_type = a.streaming_data['adaptiveFormats'][-1]['mimeType'].split(';')[
        0].split('/')[1]
    threads = []
    for url, typ, size, t in zip([vid, aud], [vid_type, aud_type], [vid_size, aud_size], ['v', 'a']):
        threads.append(Thread(target=download, args=(
            url, destination, t+file_name, typ, maN, size)))
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    cwd = os.getcwd()
    os.chdir(destination)
    os.system(
        f'ffmpeg -y -i "v{file_name}.{vid_type}" -i "a{file_name}.{aud_type}" -c copy "{file_name}.{vid_type}"')
    os.remove(f'v{file_name}.{vid_type}')
    os.remove(f'a{file_name}.{aud_type}')
    os.chdir(cwd)
    prGreen(f'Downloaded {file_name} by {a.author}')


def playlist_to_mp3(playlist_link, file_name):
    """Gets all YouTube audio in a playlist and converts to mp3."""
    p = pt.Playlist(playlist_link)
    for url in p.video_urls:
        # youtube_to_mp3(url, file_name)
        th = Thread(target=youtube_to_mp3, args=(url, file_name, True, True))
        th.start()


def search(terms):
    if isinstance(terms, str):
        terms = (terms,)
    ytmusic = YTMusic()
    links = []
    for term in terms:
        print(f'\rFinding {term}\t\t', end='\r')
        search = ytmusic.search(term)
        for i in search:
            if i['resultType'] in ('video', 'song'):
                inp = i['videoId']
                if i['resultType'] == 'song':
                    print(f'\rFound {i["title"]}\t\t')
                    break
        links.append(f'https://www.youtube.com/watch?v={inp}')
    return links


if __name__ == '__main__':
    if DEBUG:
        sys.argv.extend(
            ['-d', 'https://www.youtube.com/watch?v=08rXf8TtnLA', 'D:/Music'])
    os.chdir(os.path.dirname(SELF_FILE))
    if len(sys.argv) > 1:
        if sys.argv[1] == '-s':
            links = sys.argv[2:-1]
            file = sys.argv[-1]
        elif sys.argv[1] == '-p':
            playlist_to_mp3(sys.argv[2], sys.argv[-1])
            links = ()
        elif sys.argv[1] == '-d':
            if sys.argv[2][0] == '-':
                for link in sys.argv[3:-1]:
                    download_video(link, sys.argv[-1], vformat=sys.argv[2][1:])
            else:
                for link in sys.argv[2:-1]:
                    download_video(link, sys.argv[-1])
            links = ()
        else:
            links = search(sys.argv[1:-1])

            file = sys.argv[-1]
    else:
        # playlist_to_mp3(
        #     'https://www.youtube.com/playlist?list=PLeiSaiBpCZRHtuc-cCLGHMzAPH4AGszvn', 'D:/Sounds')
        # youtube_to_mp3('https://www.youtube.com/watch?v=I9mslglBcgU')
        links = ()
        file = 'D:/Music'
    for i in links:
        if DEBUG:
            youtube_to_mp3(i, file)
        else:
            Thread(target=youtube_to_mp3, args=(i, file)).start()
