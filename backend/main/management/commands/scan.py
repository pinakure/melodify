from django.core.management.base import BaseCommand, CommandError
from main.models import Song, Album, Artist, Playlist, Tag, Genre
from datetime import datetime, timedelta
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
INDENT_SIZE = 2
PATH_SEP = '\\' #os.path.sep

def load_array(file):
    payload = []
    with open(file, "r") as file:
        payload = file.read().split('\n')
        return payload

def load_dict(file):
    payload = {}
    with open(file, "r") as file:
        elements = file.read().split('\n')
    for element in elements:
        if len(element)==0:continue
        items = element.split('=')
        key = items[0]
        value = items[1].split(',')
        payload[key] = [ x.strip() for x in value ]
    return payload

FORBIDDEN_FOLDERS   = load_array('config/forbidden_folders.lst')
FORBIDDEN_TAGS      = load_array('config/forbidden_tags.lst')
FORBIDDEN_PREFIXES  = load_array('config/forbidden_prefixes.lst')
CODENAME_PREFIXES   = load_array('config/codename_prefixes.lst')
ARTIST_ALIASES      = load_dict('config/artist_aliases.lst')

EMOJI_REPLACEMENT = {
    '♥' : '❤',
    '♥' : '❤️',
}

FORBIDEN_CHARACTERS = [
    '/',
    '\\',
    '?',
    '!',
    '*',
    '~',
]

def sanitize_filename(text):
    for target in FORBIDEN_CHARACTERS:
        text = text.replace(target, '')
    return text                        

def get_sanitized_year(year : str):
    year = year.split('-')[0]
    if int(year)<1000: return "1000"
    return year

def get_hash(path : str):
    """Devuelve un hash de 128 caracteres ASCII (SHA-512 en hex) para un fichero MP3."""
    sha = hashlib.sha512()
    with open(path, "rb") as f:
        # Leer en bloques para archivos grandes
        for chunk in iter(lambda: f.read(8192), b""):
            sha.update(chunk)
    return sha.hexdigest()  # 128 caracteres ASCII

def is_codename(tag: str) -> bool:
    """Devuelve True si la tag es un codename."""
    for prefix in CODENAME_PREFIXES:
        if len(prefix)==0:continue
        if tag.startswith(prefix) : return True
    return False

def is_ignored_path(path: str) -> bool:
    """Devuelve True si la ruta está dentro de alguna carpeta ignorada."""
    p = Path(path).resolve()

    # Comprobamos cada parte del path
    for part in p.parts:
        for folder in FORBIDDEN_FOLDERS:
            if len(folder)==0:continue
            if part.startswith(folder):return True

    return False

def is_comment_tag(tag: str) -> bool:
    """Devuelve True si la tag tiene espacios"""
    return " " in tag

def is_forbidden_tag(tag: str) -> bool:
    """Devuelve True si la tag está prohibida."""
    for fb in FORBIDDEN_TAGS:
        if fb == tag: return True
    for fb in FORBIDDEN_PREFIXES:
        if len(fb)==0:continue
        if tag.startswith(fb): return True
    return False

def is_number(var):
    try:
        test = int(var)
        return True
    except:
        return False

def is_timestamp(tag):
    if len(tag) == 4:
        # YYYY
        if is_number(tag):
            return f'{tag}0101'
    if len(tag) == 7:
        # YYYY-MM
        if is_number(tag[0:4]):
            if is_number(tag[5:7]):
                return f'{tag[0:4]}{tag[5:7]}01'
        # MM-YYYY
        else:
            if is_number(tag[0:2]):
                if is_number(tag[3:7]):
                    return f'{tag[3:7]}{tag[0:2]}01'
        return ''
    if len(tag) == 8:
        if is_number(tag[0:6]):
            # YYYYMMXX
            if not is_number(tag[6:8]):
                return f'{tag[0:4]}{tag[4:6]}01'
            # YYYYMMDD
            else:
                return f'{tag[0:4]}{tag[4:6]}{tag[6:8]}'
        # YYYYXXXX
        else:
            if is_number(tag[0:4]):
                return f'{tag[0:4]}0101'

        # DD-MM-YY
        if is_number(tag[0:2]):
            if is_number(tag[3:5]):
                if is_number(tag[6:8]):
                    return f'20{tag[0:2]}{tag[3:5]}{tag[6:8]}'
        return ''
    if len(tag) == 10:
        # 0000-00-00
        if is_number(tag[0:4]):
            if is_number(tag[5:7]):
                if is_number(tag[8:10]):
                    return f'{tag[0:4]}{tag[5:7]}{tag[8:10]}'
        # 00-00-0000
        if is_number(tag[0:2]):
            if is_number(tag[3:5]):
                if is_number(tag[6:10]):
                    return f'{tag[6:10]}{tag[3:5]}{tag[0:2]}'
        return ''
    return ''

def sanitize_tag(tag, song):
    if is_forbidden_tag(tag):
        return ""
    if is_codename(tag):
        song.codename = tag
        return ""
    if is_comment_tag(tag):
        song.comment += tag
        return ""

    timestamp = is_timestamp(tag)
    if len(timestamp) > 0:
        print("\n")
        print(song.filename)
        print(timestamp)
        song.timestamp = timezone.make_aware(datetime(int(timestamp[0:4]),int(timestamp[4:6]),int(timestamp[6:8])))
        return ""
    if is_number(tag):
        return ""
    tag = tag.replace(' - ', ', ')
    for emoji,key in EMOJI_REPLACEMENT.items():
        tag = tag.replace(key, emoji)

    tag = tag.rstrip()
    tag = tag.rstrip('.')
    return tag

def extract_id3_tags(filepath):
    """Devuelve un diccionario con los metadatos ID3 de un archivo MP3."""
    try:
        audio = MP3(filepath)
        tags = ID3(filepath)
        def get_comments():
            target_tags = [
                'COMM::eng',
                'COMM::esp',
                'COMM::jap',
                #'COMM:ID3v1 Comment:eng',
            ]
            comments = []
            for t in target_tags:
                for comment in get_all(t):
                    comments.append(comment)
            comments = ", ".join(comments)
            return comments

        def get(tag):
            return tags[tag].text[0] if tag in tags else None

        def get_picture():
            return tags.get("APIC:").data if 'APIC:' in tags else None,

        def get_all(tag):
            return tags[tag].text if tag in tags else []

        date = get("TDRC") or get("TYER")
        try:
            date = date.strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            date = str(date) if date else None
                
        return {
            "file"          : filepath,
            "title"         : get("TIT2"),
            "artist"        : get("TPE1"),
            "album"         : get("TALB"),
            "track_number"  : get("TRCK"),
            "picture"       : get_picture(),
            "comments"      : get_comments(),
            "genre"         : get("TCON"),
            "rating"        : tags["POPM:Windows Media Player 9 Series"].rating if "POPM:Windows Media Player 9 Series" in tags else None,
            "key"           : get("TKEY"),
            "year"          : date,
            "bpm"           : get("TBPM"),
            "composer"      : get("TCOM"),
            "disc_number"   : get("TPOS"),
            "length_seconds": int(audio.info.length) if audio.info else None,
            "bitrate"       : audio.info.bitrate if audio.info else None,
            "duration"      : timedelta(seconds=audio.info.length),
        }
    except Exception as e:
        print("ID3:"+str(e))
        return {
            "file": filepath,
            "error": str(e)
        }

def dump_picture(filename, data):
    # Guarda los datos binarios de la imagen en un archivo
    with open(filename, 'wb') as img_file:
        img_file.write(data)

class Command(BaseCommand):
    help = "Scans specified path looking for mp3 files to be scanned and added to the media library"

    def add_arguments(self, parser):
        parser.add_argument("scan_path", nargs="+", type=str)
        parser.add_argument("--force", '-f', default=False,nargs="*", type=bool)

    def echo(self, text, indent=0):
        self.stdout.write(" "*(indent*INDENT_SIZE)+text)

    def get_song(self, path : str):
        try:
            return Song.objects.filter(filename=path).get()
        except Exception:
            return None



    def get_or_create_artist(self, artist_name, info):
        
        if artist_name is None: return None
        artist_name = artist_name.rstrip().lstrip()
        # Remove featuring from artist name
        artist_name = artist_name.split('Ft.')[0]
        artist_name = artist_name.split('Feat.')[0]
        artist_name = artist_name.split('feat.')[0]
        artist_name = artist_name.split('ft.')[0]
        artist_name = artist_name.lstrip(' ').rstrip(' ')
        
        if len(artist_name)==0: return None
        try:
            artist = Artist.objects.filter( name__iexact=artist_name ).get()
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
        genre_name=genre_name.strip().lower().title()
        if len(genre_name)==0: return None
        try:
            genre = Genre.objects.filter( name__iexact=genre_name ).get()
            return genre
        except Exception as e:
            genre = Genre()
            genre.name = genre_name
            genre.save()
            self.echo(f'Created genre "{ genre_name }"')
            return genre

    def get_or_create_tags(self, tags_text, song=None):
        tags = []
        if tags_text is None: return tags
        tag_list = tags_text.split(', ')
        res = []
        [res.append(val) for val in tag_list if val not in res]
        tag_list = res
        for tag_token in tag_list:
            tag = None
            tag_token = sanitize_tag( tag_token, song )
            if len(tag_token) == 0: continue
            try:
                tag = Tag.objects.filter( name=tag_token ).get()
            except Exception as e:
                tag = Tag()
                tag.name = tag_token
                tag.save()
                self.echo(f"Created tag {tag_token}", indent=1)
            tags.append(tag)
        return tags

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
            album.save()
            self.echo(f'Created album "{album_name}"')
            return album

    def add_song_error(self, song, exception, error=True):
        song.errors = song.errors + str(exception) + '\n'
        if error:
            song.error = error

    def setup_song(self, song, info : dict, hash : str):
        song.hash    = hash
        song.errors  = ''
        song.error   = False
        song.comment = ''
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
            song.duration = info.get('duration')
        except Exception as e:
            song.duration = 1
            self.add_song_error(song, f"DURATION:{str(e)}", error=False)

        try:
            song.track_number   = int(info.get('track_number'))
        except Exception as e:
            self.add_song_error(song, f"TRACK:{str(e)}", error=False)

        try:
            song.timestamp = timezone.make_aware(datetime(int(get_sanitized_year(info.get('year') or "1000")), 1, 1))
            if song.timestamp.year == 1000: song.timestamp = None
        except Exception as e:
            self.add_song_error(song, f"TRACK:{str(e)}")
        try:
            song.album = self.get_or_create_album(info.get('album'), info)
        except Exception as e:
            self.add_song_error(song, f"ALBUM:{str(e)}")

        try:
            song.artist = self.get_or_create_artist( info.get('artist'), info)
            if song.album:
                song.album.artists.add(song.artist)
                song.album.save()
        except Exception as e:
            self.add_song_error(song, f"ARTIST:{str(e)}")

        try:
            song.genre = self.get_or_create_genre( info.get('genre'), info)
            if song.album:
                song.album.genres.add(song.genre)
                song.album.save()
        except Exception as e:
            self.add_song_error(song, f"GENRE:{str(e)}")

        try:
            song.bpm = info.get('bpm')
        except Exception as e:
            self.add_song_error(song, f"BPM:{str(e)}")

        try:
            song.key = info.get('key')
        except Exception as e:
            self.add_song_error(song, f"KEY:{str(e)}")

        picture = info.get('picture')[0] if 'picture' in info.keys() else None
        if picture is not None:
            try:
                if song.picture == '':
                    sha = hashlib.sha512()
                    sha.update(picture)
                    filename = sha.hexdigest()  # 128 caracteres ASCII
                    path = os.path.join('.', "media", "songs", f'{filename}.png')
                    dump_picture(path, picture)
                    song.picture = f'/media/songs/{filename}.png'
            except Exception as e:
                print(picture)
                print("SETUPSONGPIC:" + str(e))
                quit()
                self.add_song_error(song, f"PICTURE:{str(e)}")

            try:
                if song.album is not None:
                    if song.album.picture is None:
                        filename = sanitize_filename(song.album.name)
                        path = os.path.join('.', "media", "albums", f'{filename}.png')
                        dump_picture(path, picture)
                        song.album.picture = f'/media/albums/{filename}.png'
                        song.album.save()
            except Exception as e:
                print("SETUPALBUMPIC:" + str(e))
                quit()
                self.add_song_error(song, f"PICTURE:{str(e)}")

        song.save()

        for tag in self.get_or_create_tags( info.get('comments'), song):
            try:
                song.tags.add(tag)
            except Exception as e:
                self.add_song_error(song, f"TAGS:{str(e)}")

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

    def scan(self, folder, force=False):
                        
        """Escanea una carpeta recursivamente en busca de archivos MP3."""
        results = []
        self.folder = folder
        for root, _, files in os.walk(folder):
            if is_ignored_path(root):
                continue
            tabs = "  " * len(root.split(folder)[1].split("\\"))
            last = root.split(folder)[1].split("\\")[-1]
            # print(("  "*50)+"\r"+tabs+root.split(folder)[1].lstrip('\\').lstrip('/'))
            print(("  "*50)+"\r"+tabs+last.lstrip('\\').lstrip('/'))
            for f in files:
                if f.lower().endswith(".mp3"):
                    print(("  "*50)+"\r"+f, end="\r")
                    path = os.path.join(root, f)
                    hash = get_hash(path)
                    # check whether or not the song object exists
                    id = os.path.join(root, f)
                    song = self.get_song(id)
                    if (song is not None) and (song.hash == hash) and (not song.error) and (not force):
                        continue
                    info = extract_id3_tags(path)
                    if song is None:
                        self.create_song(id , info, hash)
                    else:
                        self.update_song(id, info, hash)
                    results.append(info)
        return results

    def handle(self, *args, **options):
        FORCE_ANALYSIS = False
        MUSIC_FOLDER = options["scan_path"][0] or "/mnt/c/Users/smiker/Music/"   # <-- cámbialo
        if options['force'] is not False:
            print(("*"*80)+'\n'+" Forcing analysis...\n"+("*"*80))
            force = True
                        
        self.echo("Scanning media...")
        self.echo(f"Folder: {MUSIC_FOLDER}")
        results = self.scan(MUSIC_FOLDER, FORCE_ANALYSIS)

        self.echo("\n"+f"Scan complete: {len(results)} files.")