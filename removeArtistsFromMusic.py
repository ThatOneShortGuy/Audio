'''Removes the artists from the lyrics.
ex.
Keep an anime bitch all on me, yah

[Chorus: Shiki-TMNS]
Keep an anime bitch all on me
Shawty look sexy like a damn daki

-------------- to --------------- 

Keep an anime bitch all on me, yah
Keep an anime bitch all on me
Shawty look sexy like a damn daki
'''
import os

# os.chdir(r'C:\Users\braxt\OneDrive\Music\Lyrics')
os.chdir('D:/Music/Lyrics')

for file in os.listdir():
    inPart = False
    start = 0
    text = open(file, 'rb').read()
    removables = b''
    for i, letter in enumerate(text):
        if letter in b'[' and not inPart:
            start = i
            inPart = True
        elif letter in b']' and inPart:
            text = text.replace(removables+b']', b'')
            inPart = False
            removables = b''
        if inPart:
            removables += chr(letter).encode()
    text = text.replace(b'<N><N><N>', b'<N>').replace(b'\n', b'<N>')
    with open(file, 'wb') as f:
        f.write(text)
