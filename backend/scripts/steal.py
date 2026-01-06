# -*- coding: utf-8 -*-
from pathlib        import Path
import shutil
import sys
import os
import io
import re
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))                                      # Add backend directory to the sys.path so Python can find 'backend.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings') # Set the environment variable for your Django settings
import django
django.setup()                                                      # Setup Django
from django.conf    import settings
from main.utils     import Utils, debug
debug("-"*80)
debug(f"STEAL :: Imported Django")
from spotdl         import Spotdl
debug(f"STEAL :: Imported Spot DL")
import yt_dlp
debug(f"STEAL :: Imported YTDLP")
import requests
debug(f"STEAL :: Module Initialization Complete")
debug("-"*80)
#------------------------------------------------------------------------------
help            = "Steal"
initialized     = False
client_id       = settings.SPOTIFY_CLIENT_ID        # move this data to user 
client_secret   = settings.SPOTIFY_CLIENT_SECRET    # move this data to user profile
debug(f"STEAL :: Initializing Spot DL")
spotdl          =  Spotdl(
    client_id       = client_id, 
    client_secret   = client_secret, 
    no_cache        = True,
)
LIBRARY_ROOT    = Utils.library_path()

debug(f"STEAL :: Spot DL Initialized")

def clean_path_name(name):
    # 1. Eliminar caracteres prohibidos en Windows: \ / : * ? " < > |
    name = re.sub(r'[\\/:*?"<>|]', '', name)
    # 2. Eliminar espacios o puntos al final (causan WinError 123)
    name = name.strip().rstrip('.')
    # 3. Forzar UTF-8 para manejar la 'ñ' correctamente
    return name.encode('utf-8', 'ignore').decode('utf-8')

def ytSearch(url, max_resultados=1):
    # Configuración de opciones para la búsqueda
    ydl_opts = {
        'quiet'         : True,       # No mostrar logs innecesarios
        'no_warnings'   : True,
        'extract_flat'  : True,       # Extraer metadatos básicos rápidamente
        'format'        : 'bestaudio/best',
    }
    busqueda = f"ytsearch{max_resultados}:{url}"
    payload = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(busqueda, download=False)
            if 'entries' in info and len(info['entries']) > 0:
                for entry in info['entries']:
                    item = {
                        "name"      : f"{entry.get('title'                     ).encode('ascii', 'ignore').decode('ascii').replace("'", '´')}",
                        "artist"    : f"Youtube",
                        "album"     : f"{entry.get('uploader' , 'No Album'     ).encode('ascii', 'ignore').decode('ascii').replace("'", '´')}",
                        "url"       : f"www.youtube.com/watch?v={entry.get('id')}",
                        "type"      : f"youtube",
                    }
                    payload.append(
                        item
                    )
                    debug(f'STEAL :: entry = {item}')
                return payload
            else:
                debug(f"STEAL :: No results for '{url}'")
                return payload
        except Exception as e:
            debug(f"STEAL :: Search Error : {e}")
            return payload

def ytDownload(url):
    ydl_opts = {
        'postprocessors': [
            { 'key' : 'FFmpegExtractAudio'  , 'preferredcodec'  : 'mp3' , 'preferredquality'  : '320'},
            { 'key' : 'FFmpegMetadata'      , 'add_metadata'    : True  } ,
        ],
        'format'        : 'bestaudio/best',
        'outtmpl'       : os.path.join('.', '%(title)s.%(ext)s'),
        'quiet'         : True,
        'noprogress'    : True,
        'no_warnings'   : True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            debug(f"STEAL :: Downloading from youtube: {url}")
            info = ydl.extract_info(url, download=True)
            #ydl.download([])
            debug(f'STEAL ::       info.id = {info.get('id')}')
            debug(f'STEAL ::    info.title = {info.get('title')}')
            debug(f'STEAL :: info.filepath = {info['requested_downloads'][0]['filepath']}')
            temp_file = Path(info['requested_downloads'][0]['filepath'])
            dst_dir   = LIBRARY_ROOT / 'Y' / 'Youtube'
            dest_file = dst_dir / f"{info['title'].split('.')[0]}.mp3"
            debug(f'STEAL :: move {str(temp_file)} ==> {str(dest_file)}')
            os.makedirs(os.path.dirname(dest_file), exist_ok=True)
            shutil.move(str(temp_file), str(dest_file))
            return [ 'Youtube' ]
        except Exception as e:
            debug(f"STEAL :: Download Error : {e}")
            return []

def searchSong(url):
    debug(f"STEAL :: searching {url}...")
    song_objs = spotdl.search([url])
    debug(f"STEAL :: search finished, {len(song_objs)} songs found.")
    payload = []
    for song in song_objs:
        payload.append({ 
            "name"  : f"{song.name.replace("'", '´')}",
            "artist": f"{song.artist.replace("'", '´')}",
            "album" : f"{song.album_name.replace("'", '´')}",
            "url"   : f"{song.url       }",
            "type"  : "spotify",
        }) 
    if not 'open.spotify.com' in url:
        for song in ytSearch(url, 3):
            payload.append(song)
    return payload

def getSong(url):
    payload = []
    debug("-"*80)
    if 'www.youtube.com' in url:
        debug(f"STEAL :: Downloading from youtube {url}...")
        payload = ytDownload(url)
        return payload
    debug(f"STEAL :: Downloading from spotify {url}...")
    song_objs = spotdl.search([url])
    for song in song_objs:
        try:
            cover        = song.cover_url
            response     = requests.get(cover)
            if response.status_code == 200:
                ruta_destino = os.path.join('media', 'songs', f'{clean_path_name(song.name)}.png')
                with open(ruta_destino, 'wb') as f:
                    f.write(response.content)
        except Exception as e:
            debug(f"STEAL :: Failed to Download Coverart : {str(e)}")
        try:
            artist_clean = clean_path_name(song.artists[0])
            album_clean  = clean_path_name(song.album_name)
            title_clean  = clean_path_name(song.name) + ".mp3"
            letter       = artist_clean[0].upper() if artist_clean else "#"

            dst_dir     = Path(os.path.join(LIBRARY_ROOT, letter, artist_clean, album_clean))
            dest_file   = Path(os.path.join(dst_dir, title_clean))

            if dest_file.exists():
                debug(f"STEAL :: Skipping: {title_clean} ya existe.")
                continue

            download_results = spotdl.download_songs([song])
            temp_path_str = download_results[0][1] # ruta real en disco

            if temp_path_str is None:
                continue

            temp_file = Path(temp_path_str)

            # Crear carpetas y mover
            dst_dir.mkdir(parents=True, exist_ok=True)
            debug(f"STEAL :: temp_file = '{temp_file}'")
            debug(f"STEAL :: dest_file = '{dest_file}'")
            debug(f"STEAL :: moviendo de {temp_file} a {dest_file}")
            # Usamos str() para compatibilidad total con shutil en Windows
            shutil.move(temp_file, dest_file)
            
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
        debug(f"STEAL :: Searching '{URL}'")
        payload = searchSong(URL)
else:
    debug(f"STEAL :: Downloading '{URL}'")
    payload = getSong(URL)
debug(f"STEAL :: Finished processing '{URL}'")
debug(f'STEAL :: payload={payload}'.encode('ascii', 'ignore').decode('ascii'))
print(f'{payload}'.encode('ascii', 'ignore').decode('ascii'))