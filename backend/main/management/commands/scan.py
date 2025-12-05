from django.core.management.base import BaseCommand, CommandError
from main.models import Song, Album, Artist, Playlist, Tag, Genre
from datetime import datetime
from django.utils import timezone

#!/usr/bin/env python3
import os
import time
import json
import hashlib
from pathlib import Path

from mutagen.mp3 import MP3
from mutagen.id3 import ID3


# ============
# CONFIG
# ============
OUTPUT_JSON = "scan_results.json"            # opcional: para depuración
INDENT_SIZE = 2
PATH_SEP = '\\' #os.pathsep
IGNORE_FOLDERS = [
    '$RECYCLE.BIN',
    '.android_secure',
    '.album',
    '.artist',
    '.binaural',
    '.casette-eps',
    '.chiptune',
    '.genre',
    '.mini_vinyls',
    '.ost',
    '.podcast',
    '.rip',
    '.scripts',
    '.sessions',
    '.source',
    '.trash',
    '.video',
    '_Serato_',
    '_Serato_Backup',
    'Android',
    'LOST_DIR',
    'System Volume Information',
    'sorted',
    'unsorted',
]

def get_sanitized_year(year : str):
    year = year.split('-')[0]
    return year

def is_ignored_path(path: str) -> bool:
    """Devuelve True si la ruta está dentro de alguna carpeta ignorada."""
    p = Path(path).resolve()

    # Comprobamos cada parte del path
    for part in p.parts:
        if part in IGNORE_FOLDERS:
            return True

    return False

def extract_id3_tags(filepath):
    """Devuelve un diccionario con los metadatos ID3 de un archivo MP3."""
    try:
        audio = MP3(filepath)
        tags = ID3(filepath)
        # print(tags )
        # quit()

        def get_comments():
            target_tags = [
                'COMM::eng',
                'COMM::esp',
                'COMM::jap',
                'COMM:ID3v1 Comment:eng',
            ]
            comments = []
            for t in target_tags:
                for comment in get_all(t): comments.append(comment)
            comments = ", ".join(comments)
            return comments

        def get(tag):
            return tags[tag].text[0] if tag in tags else None
        
        def get_all(tag):
            return tags[tag].text if tag in tags else []

        date = get("TDRC") or get("TYER")
        try:
            date = date.strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            date = str(date) if date else None

        return {
            "file": filepath,
            "title": get("TIT2"),
            "artist": get("TPE1"),
            "album": get("TALB"),
            "track_number": get("TRCK"),
            "comments": get_comments(),
            "genre": get("TCON"),
            "rating": tags["POPM:Windows Media Player 9 Series"].rating if "POPM:Windows Media Player 9 Series" in tags else None,
            "key": get("TKEY"),
            "year": date,
            "bpm": get("TBPM"),
            "composer": get("TCOM"),
            "disc_number": get("TPOS"),
            "length_seconds": int(audio.info.length) if audio.info else None,
            "bitrate": audio.info.bitrate if audio.info else None,
        }
    except Exception as e:
        return {
            "file": filepath,
            "error": str(e)
        }


def get_hash(path : str):
    """Devuelve un hash de 128 caracteres ASCII (SHA-512 en hex) para un fichero MP3."""
    sha = hashlib.sha512()

    with open(path, "rb") as f:
        # Leer en bloques para archivos grandes
        for chunk in iter(lambda: f.read(8192), b""):
            sha.update(chunk)

    return sha.hexdigest()  # 128 caracteres ASCII



class Command(BaseCommand):
    help = "Scans specified path looking for mp3 files to be scanned and added to the media library"

    def add_arguments(self, parser):
        parser.add_argument("scan_path", nargs="+", type=str)

    def echo(self, text, indent=0):
        self.stdout.write(" "*(indent*INDENT_SIZE)+text)

    def get_song(self, path : str):
        try:
            return Song.objects.filter(filename=path).get()
        except Exception:
            return None
        
    def get_song_artists( self, info ):
        artist_name = info.get('artist')
        results = []
        try:
            results.append( Artist.objects.filter( name=artist_name ).get() )
        except: 
            try:
                results.append( Artist.objects.filter( aliases__icontains=artist_name.lower() ).get()) 
            except:
                pass
        return results
    
    def get_or_create_artist(self, artist_name, info):
        if artist_name is None: return None
        try:
            artist = Artist.objects.filter( name=artist_name ).get()
            return artist
        except Exception as e:
            try:
                artist = Artist.objects.filter( aliases__icontains=artist_name.lower() ).get()
                return artist
            except Exception as e:
                artist = Artist()
                artist.name     = artist_name
                artist.aliases  = ''
                artist.bio      = ''
                artist.picture = None
                # artist.genres  = None
                artist.save()
                self.echo(f'Created artist "{ artist_name }"')
                return artist

    def get_or_create_genre(self, genre_name, info):
        if genre_name is None: return None
        try:
            genre = Genre.objects.filter( name=genre_name ).get()
            return genre
        except Exception as e:
            genre = Genre()
            genre.name = genre_name
            genre.save()
            self.echo(f'Created genre "{ genre_name }"')
            return genre

    def get_or_create_album(self, album_name, info):
        if album_name is None: return None
        try:
            album = Album.objects.filter( name=album_name ).get()
            return album
        except Exception as e:
            album = Album()
            album.name = album_name
            album.codename = info.get('codename') or None
            album.brief = ''
            album.picture = None
            album.booklet = None
            album.edition = None
            album.limited = False
            album.edition = 'Vanila'
            # album.artists = None
            # album.genres = None
            album.save()
            self.echo(f'Created album "{album_name}"')
            return album
    
    def add_song_error(self, song, exception, error=True):
        song.errors = song.errors + str(exception) + '\n'
        if error: 
            song.error = error    

    def setup_song(self, song, info : dict, hash : str):
        song.hash  = hash
        song.errors = ''
        song.error = False

        try:            
            song.title = info.get('title')
            if song.title is None:
                song.error = True
                song.errors = song.errors + "Title not found. Using filename as fallback.\\n"
                song.title = str(song.filename).split(PATH_SEP)[-1]
                # self.echo(song.title)
                # quit()
        except Exception as e:
            self.echo(str(e))
            self.add_song_error(song, f"TITLE:{str(e)}")

        try:
            song.track_number   = int(info.get('track_number')) 
        except Exception as e:
            self.add_song_error(song, f"TRACK:{str(e)}", error=False)

        try:
            song.timestamp = timezone.make_aware(datetime(int(get_sanitized_year(info.get('year') or "1900")), 1, 1))
        except Exception as e:
            self.add_song_error(song, f"TRACK:{str(e)}")
            
        try:
            song.album = self.get_or_create_album(info.get('album'), info)
        except Exception as e:
            self.add_song_error(song, f"ALBUM:{str(e)}")

        try:
            song.artist = self.get_or_create_artist( info.get('artist'), info)
        except Exception as e:
            self.add_song_error(song, f"ARTIST:{str(e)}")
        
        try:
            song.genre = self.get_or_create_genre( info.get('genre'), info)
        except Exception as e:
            self.add_song_error(song, f"GENRE:{str(e)}")

        # try:
        #     song.tags = self.get_or_create_genre( info.get('genre'), info)
        # except Exception as e:
        #     self.add_song_error(song, f"GENRE:{str(e)}")


        song.save()

    def update_song(self, path : str, info : dict, hash : str):
        song = Song.objects.filter(filename=path).get()
        self.setup_song( song, info , hash)
        self.echo(f'Updated song {path}', indent=1)
        
    def create_song(self, path : str, info : dict, hash : str):
        song = Song()
        song.filename = path
        self.setup_song( song, info , hash)
        self.echo(f'Created song "{path}"', indent=1)
        
    def scan(self, folder):
        """Escanea una carpeta recursivamente en busca de archivos MP3."""
        results = []

        for root, _, files in os.walk(folder):
            if is_ignored_path(root):
                continue
            # self.echo(root.strip(folder))
            print(("  "*50)+"\r"+root.split(folder)[1].lstrip('\\').lstrip('/'))
            for f in files:
                if f.lower().endswith(".mp3"):
                    # self.echo(f, indent=1)
                    print(("  "*50)+"\r"+f, end="\r")
                    path = os.path.join(root, f)
                    hash = get_hash(path)
                    # check whether or not the song object exists
                    id = os.path.join(root, f)
                    song = self.get_song(id) 
                    if (song is not None) and song.hash == hash and not song.error: 
                        continue
                    info = extract_id3_tags(path)
                    if song is None: 
                        self.create_song(id , info, hash)
                    else:                        
                        # if not song.error:
                        #     self.echo(hash)
                        #     self.echo(song.hash)
                        self.update_song(id, info, hash)
                    results.append(info)
        return results

    def handle(self, *args, **options):
        
        MUSIC_FOLDER = options["scan_path"][0] or "/mnt/c/Users/smiker/Music/"   # <-- cámbialo

        self.echo("Scanning media...")
        self.echo(f"Folder: {MUSIC_FOLDER}")
        results = self.scan(MUSIC_FOLDER)

        # Puedes guardar resultados o procesarlos aquí
        with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        self.echo(f"Scan complete: {len(results)} files.")