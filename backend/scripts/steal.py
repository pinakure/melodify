# -*- coding: utf-8 -*-
from pathlib import Path
import shutil
import sys
import os
import io
import re

# 1. Add your backend directory to the sys.path so Python can find 'backend.settings'
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# 2. Set the environment variable for your Django settings
# Replace 'backend.settings' with the actual path to your settings.py (e.g., 'melodify.settings')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# 3. Setup Django
import django
django.setup()

from django.conf import settings
from main.management.commands.scan import saferead, debug
from spotdl import Spotdl

help            = "Steal"
initialized     = False
client_id       = settings.SPOTIFY_CLIENT_ID        # move this data to user 
client_secret   = settings.SPOTIFY_CLIENT_SECRET    # move this data to user profile
spotdl          =  Spotdl(
    client_id = client_id, 
    client_secret = client_secret, 
    no_cache=True,
)

def clean_path_name(name):
    # 1. Eliminar caracteres prohibidos en Windows: \ / : * ? " < > |
    name = re.sub(r'[\\/:*?"<>|]', '', name)
    # 2. Eliminar espacios o puntos al final (causan WinError 123)
    name = name.strip().rstrip('.')
    # 3. Forzar UTF-8 para manejar la 'ñ' correctamente
    return name.encode('utf-8', 'ignore').decode('utf-8')

def searchSong(url):
    debug(f"STEAL :: searching {url}...")
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
                debug(f"STEAL :: Skipping: {title_clean} ya existe.")
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
            
            debug(f"STEAL :: temp_file = '{temp_file}'")
            debug(f"STEAL :: dest_file = '{dest_file}'")
            debug(f"STEAL :: moviendo de {temp_file} a {dest_file}")
            # Usamos str() para compatibilidad total con shutil en Windows
            shutil.move(str(temp_file), str(dest_file))
            
            if artist_clean not in payload:
                payload.append(artist_clean)

        except Exception as e:
            debug(f"STEAL :: Error con '{song.name}': {str(e)}")
    return payload

payload = ''
URL = sys.argv[1]
debug(f"STEAL :: Processing '{URL}'")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
if len(sys.argv) >2:
    if sys.argv[2]=='--search_only':
        payload = searchSong(URL)
else:
    payload = getSong(URL)
print(payload)