from spotdl import Spotdl
import shutil
import os 
import sys

def clean(songname):
    songname = songname.replace('?', '')
    songname = songname.replace(':', '')
    songname = songname.replace('*', '')
    songname = songname.replace('/', '-')
    songname = songname.replace('\\', '')
    return songname

help            = "Steal"
initialized     = False
spotdl          =  Spotdl(
    client_id="dc75272b15354119b9df60392848cc6a", 
    client_secret="76d4dfef594f4625bd68b8068a574289", 
    no_cache=True
)


def searchSong(url):
    song_objs = spotdl.search([url])
    payload = []
    for song in song_objs:
        payload.append({ 
            'name'   : song.name,
            'artist' : song.artist,
            'url'    : song.url,
            'album'  : song.album_name,
        }) 
    return payload

def getSong(url):
    song_objs = spotdl.search([url])

    with open('config/library-root.cfg', 'r') as f:
        LIBRARY_ROOT = f.read()
    payload = []

    for song in song_objs:
        print(f'{song.artist}, {song.name}')
        print("-"*80)
        
        try:
            artists  = ", ".join(song.artists)
            artist   = artists.split(',')[0]
            letter   = artist[0].upper()
            album    = clean(song.album_name)
            title    = clean(f'{song.name}.mp3')
            dest     = os.path.join(LIBRARY_ROOT, letter, artist, album, title)
            dstpath  = os.path.join(LIBRARY_ROOT, letter, artist, album)
            if os.path.exists(os.path.join(dstpath,  title)):
                print('Skipping download, song already exists.')
                continue
            result   = spotdl.download_songs([song])[0]
            if result[1] is None:
                print(result)
                continue
            filename = clean(result[1].name)
            print(f'Move "{filename}" ---> "{dest}"')
            try:
                os.makedirs(dstpath)
            except:
                pass
            try:
                shutil.move(filename, dest)
                payload.append(artist)
            except Exception as e:
                print(str(e))
        except Exception as e:
            print(f"Error downloading '{ song.name }' : {str(e)}")
    return payload

payload = ''
URL = sys.argv[1]
if len(sys.argv) >2:
    if sys.argv[2]=='--search_only':
        payload = searchSong(URL)
else:
    print(("*"*80)+'\n'+f" Downloading {URL}..."+"\n"+("*"*80))
    payload = getSong(URL)
print(f"'''{payload}'''")
