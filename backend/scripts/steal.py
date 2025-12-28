import os
import django
import sys
from pathlib import Path

# 1. Add your backend directory to the sys.path so Python can find 'backend.settings'
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# 2. Set the environment variable for your Django settings
# Replace 'backend.settings' with the actual path to your settings.py (e.g., 'melodify.settings')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# 3. Setup Django
django.setup()

# Now you can safely import settings and spotDL
from django.conf import settings
from spotdl import Spotdl
import shutil


def saferead(filename, read_mode='r'):
    with open(filename, read_mode) as f:
        return f.read()
    
def debug(text):
    #return
    with open('/var/log/melodify.log', 'a') as f:
        f.write(text+'\n')
    
def clean(songname):
    songname = songname.replace('?', '')
    songname = songname.replace('"', '')
    songname = songname.replace(':', '')
    songname = songname.replace('*', '')
    songname = songname.replace('/', '-')
    songname = songname.replace('\\', '')
    return songname

help            = "Steal"
initialized     = False
client_id       = settings.SPOTIFY_CLIENT_ID
client_secret   = settings.SPOTIFY_CLIENT_SECRET
spotdl          =  Spotdl(
    client_id = client_id, 
    client_secret = client_secret, 
    no_cache=True,
    # downloader_settings={
    #     'output' : "out.mp3"
    # }
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
    debug("-"*80)
    debug(f"STEAL :: searching {url}...")
    song_objs = spotdl.search([url])
    LIBRARY_ROOT = saferead('config/library-root.cfg')
    payload = []
    for song in song_objs:
        debug(f"STEAL ::        title = {song.name}")
        debug(f"STEAL ::        album = {song.album_name}")
        debug(f"STEAL ::       artist = {', '.join(song.artists)}")
        debug(f"STEAL :: download_url = {song.download_url}")
        try:
            artists  = ", ".join(song.artists)
            artist   = artists.split(',')[0]
            letter   = artist[0].upper()
            album    = clean(song.album_name)
            title    = clean(f'{song.name}.mp3')
            dest     = os.path.join(LIBRARY_ROOT, letter, artist, album, title)
            dstpath  = os.path.join(LIBRARY_ROOT, letter, artist, album)
            if os.path.exists(os.path.join(dstpath,  title)):
                debug(f"Skipping '{os.path.join(dstpath, title)}' : Already Exists")
                continue
            debug(f"STEAL :: Downloading song '{song}'...")
            result   = spotdl.download_songs([song])[0]
            debug(f"STEAL :: result = '{result}'")
            if result[1] is None:
                debug(f"STEAL :: Skipping '{os.path.join(dstpath, title)}' : result[1] = None'")
                continue
            filename = clean(result[1].name)
            try:
                os.makedirs(dstpath)
            except:
                debug(f"STEAL :: makedirs('dstpath') failed.'")
            try:
                debug(f"STEAL :: mv( filename = '{filename}', dest = '{dest}' )")
                shutil.move(filename, dest)
                payload.append(artist)
            except Exception as e:
                debug(str(e))
        except Exception as e:
            debug(f"Error downloading '{ song.name }' : {str(e)}")
    return payload

payload = ''
URL = sys.argv[1]
if len(sys.argv) >2:
    if sys.argv[2]=='--search_only':
        payload = searchSong(URL)
else:
    payload = getSong(URL)
print(f"'''{payload}'''")