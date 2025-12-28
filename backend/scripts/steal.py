# -*- coding: utf-8 -*-
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
from main.management.commands.scan import saferead

def debug(text):
    #return
    with open(settings.LOG_FILE, 'a') as f:
        f.write(text+'\n')

import re

def clean_path_name(name):
    # 1. Eliminar caracteres prohibidos en Windows: \ / : * ? " < > |
    name = re.sub(r'[\\/:*?"<>|]', '', name)
    # 2. Eliminar espacios o puntos al final (causan WinError 123)
    name = name.strip().rstrip('.')
    # 3. Forzar UTF-8 para manejar la 'ñ' correctamente
    return name.encode('utf-8', 'ignore').decode('utf-8')

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
client_id       = settings.SPOTIFY_CLIENT_ID        # move this data to user 
client_secret   = settings.SPOTIFY_CLIENT_SECRET    # move this data to user profile
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
    LIBRARY_ROOT = saferead('config/library-root.cfg').strip('\n')
    payload = []
    for song in song_objs:
        try:
            # 1. Limpiar metadatos para la ruta de destino
            artist_clean = clean_path_name(song.artists[0])
            album_clean  = clean_path_name(song.album_name)
            title_clean  = clean_path_name(song.name) + ".mp3"
            letter       = artist_clean[0].upper() if artist_clean else "#"

            # 2. Construir rutas seguras
            base_dir = Path(LIBRARY_ROOT).resolve()
            dst_dir  = base_dir / letter / artist_clean / album_clean
            dest_file = dst_dir / title_clean

            if dest_file.exists():
                debug(f"Skipping: {title_clean} ya existe.")
                continue

            # 3. Descargar y obtener la ruta REAL del archivo temporal
            # spotdl.download_songs devuelve una tupla (song, path_to_file)
            download_results = spotdl.download_songs([song])
            temp_path_str = download_results[0][1] # Esta es la ruta real en disco

            if temp_path_str is None:
                continue

            temp_file = Path(temp_path_str)

            # 4. Crear carpetas y mover
            dst_dir.mkdir(parents=True, exist_ok=True)
            
            debug(f"STEAL :: moviendo de {temp_file} a {dest_file}")
            # Usamos str() para compatibilidad total con shutil en Windows
            shutil.move(str(temp_file), str(dest_file))
            
            payload.append(artist_clean)

        except Exception as e:
            debug(f"Error con '{song.name}': {str(e)}")
    return payload

def oldGetSong(url):
    debug("-"*80)
    debug(f"STEAL :: searching {url}...")
    song_objs = spotdl.search([url])
    LIBRARY_ROOT = saferead('config/library-root.cfg').strip('\n')
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