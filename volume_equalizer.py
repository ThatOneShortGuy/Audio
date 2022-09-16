from soundfile import write
from librosa import load
import os
import sys
from threading import Thread


def to_ex(filename, extension, artist=None, title=None):
    """ Transforms file into the extention given """
    try:
        file, exe = os.path.splitext(filename)
        if exe == extension:
            return filename
        if isinstance(artist, str):
            album_artist = artist
        if isinstance(artist, (list, tuple)):
            album_artist = artist[1]
            artist = artist[0]
        # Convert video into .wav file
        os.system(
            f'ffmpeg -loglevel quiet -y -i "{filename}" {f"""-metadata artist="{artist}" -metadata album_artist="{album_artist}" """ if artist else ""} {f"""-metadata title="{title}" """ if title else ""} -q:a 2 -b:a 192k -id3v2_version 3 -vn "{file}{extension}"')
        os.remove(file+exe)
        return f'{file}{extension}'
    except OSError as err:
        print(err)


def equalize(filename, artist=None, title=None):
    file, exe = os.path.splitext(filename)
    minedir = to_ex(filename, '.wav') if exe != '.wav' else filename
    mine, sr = load(minedir, sr=None, mono=False)
    minevol = mine.max()
    mine *= 1/minevol
    write(minedir, mine.T, sr)
    return to_ex(minedir, exe, artist, title)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        for path in sys.argv[1:]:
            th = Thread(target=equalize, args=(path,))
            th.start()
