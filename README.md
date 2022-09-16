# Download and convert YouTube video to to mp3
- It downloads the music you want, finds the metadata, and attaches it to mp3.
- Can download whole playlists
- Uses search to find the music so long as you know the name
- Downloads video and user select download codec

This is the most used program part of this package I use personally.

[Quick Start](##quick-start)

[Advanced Guide](##advanced-guide)

## Quick Start
### Requirements
- pytube
- ytmusicapi
- lyricsgenius
- eyed3
- librosa
- soundfile

 `pip install -U pytube ytmusicapi lyricsgenius eyed3 librosa soundfile`
 
 You will also need FFMPEG installed and added to path

### Usage
Use the name of the program, then the name + artist of any song. You can do as many songs as you want so long as there is at least one. Finally, the last argument is
the location on your computer you want to download the song to.

`youtube_to_mp3.py "Name of song + artist" "Name of other song + artist"... "Location to store songs"`

Example: `youtube_to_mp3.py "Rap God Eminem" "She bad Khantrast" D:/Music`

Genius will request you use your token ID. Go to [Genius](https://genius.com/api-clients/new) and make a new API client. Once you give the program your API key,
it will store it in a file named "genius_token.txt" wherever the program is stored so you won't have to enter it again.

## Advanced Guide
Ensure you have the modules as stated in the [Quick Start Requirements](###requirements)

There are more arguments you can pass in the command for different usages.
- [-s (skip search and treat each argument as a link)](###-s)
- [-p (download playlist)](###-p)
- [-d (download video)](###-d)

### -s
This flag will treat each argument as a link and download from that link

### -p
Provide a link to a youtube playlist and the program will download all the songs in the playlist

### -d
Download the video from the music directly from YouTube! Add the direct link to the video you are referring to. You will be prompted to to select from the top
three highest resolution codecs to download from. The AVC1 (h.264) videos tend to be of the highest quality. VP09 will have a smaller file size. AV01 is a newer
codec that will likely result in a much smaller file size while still retaining high quality.

There is another flag that can be added for more specific behavior.

#### -[video format]
Specify what video format you want to download. This will eliminate the need to respond to each prompt.

\*\***NOTE**\*\* that downloading the video means that the metadata for the songs will not be retrieved.
