from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
from main.models import Song, Album, Artist, Playlist, Tag, Genre
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from pathlib import Path
from .utils import debug, saferead, safewrite, load_array, load_dict, dump_picture
from .generatelyrics import Command as GenerateLyrics
import platform
import hashlib
import os

# ============
# CONFIG
# ============
INDENT_SIZE         = 2
PATH_SEP            = os.path.sep
FORBIDDEN_FOLDERS   = load_array('forbidden_folders.lst')
FORBIDDEN_TAGS      = load_array('forbidden_tags.lst')
FORBIDDEN_PREFIXES  = load_array('forbidden_prefixes.lst')
CODENAME_PREFIXES   = load_array('codename_prefixes.lst')
ARTIST_ALIASES      = load_dict('artist_aliases.lst')

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
    ':',
    '"',
    '<',
    '>',
]

def sanitize(text):
    text = text.replace('/','')
    text = text.replace('&','and')
    text = text.replace('"','')
    return text

def sanitize_filename(text):
    for target in FORBIDEN_CHARACTERS:
        text = text.replace(target, '')
    return text    

def sanitize_name(name):
    return name.strip().lower().title()

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

def sanitize_year(year : str):
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
        if tag.lower().startswith(fb): return True
    return False

def is_number(var):
    try:
        test = int(var)
        return True
    except:
        return False

def is_timestamp(tag):
    if '/' in tag or '\\' in tag:
        return ''
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
        if is_number(tag[0:4]):
            if int(tag[0:4]) < 2500:
                if not is_number(tag[6:8]):
                    # YYYYMMXX
                    return f'{tag[0:4]}{tag[4:6]}01'
                elif not is_number(tag[4:6]):
                    # YYYYXXXX
                    if is_number(tag[0:4]):
                        return f'{tag[0:4]}0101'
                else:
                    # YYYYMMDD
                    return f'{tag[0:4]}{tag[4:6]}{tag[6:8]}'
        elif is_number(tag[0:2]):
            # DD-MM-YY
            if not is_number(tag[2]):
                if is_number(tag[3:5]):
                    if not is_number(tag[5]):
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





class Command(BaseCommand):
    help = "Scans specified path looking for mp3 files to be scanned and added to the media library"
    
    def echo(self, text):
        self.stdout.write(self.tabs+text)
    
    def add_arguments(self, parser):
        parser.add_argument("scan_path"                                 , nargs="+" , type=str  )
        parser.add_argument("--force"           , '-f', default=False   , nargs="*" , type=bool )
        parser.add_argument("--generatelyrics"  , '-g', default=False   , nargs="*" , type=bool )
        parser.add_argument("--verbose"         , '-V', default=False   , nargs="*" , type=bool )

    def resolveBasePath(self, BASEPATH):
        if platform.system() == 'Windows':
            os.system('cls')
        else:
            os.system('clear')
        BASEPARTS = BASEPATH.split(':')
        DRIVE = ''
        PATH  = ''
        if isinstance(BASEPARTS, str):
            PATH = BASEPARTS
        elif len(BASEPARTS)==1:
            # Single location ( / , /home/user/music , D: , D , D:\ ....)
            PATH = BASEPARTS[0]
        else:
            # Drive and (optional) Path
            [DRIVE, PATH] = BASEPARTS
            PATH = PATH.lstrip(os.path.sep)
            PATH = PATH.rstrip(os.path.sep)
        if PATH == '': 
            PATH = os.path.sep
        # Remove duplicated os.path.sep in the path
        PATH_PIECES = PATH.split(os.path.sep)
        PATH = ''
        for p in PATH_PIECES:
            if not len(p): continue 
            PATH += p
            PATH += os.path.sep
        MUSIC_FOLDER = os.path.join(f'{ DRIVE }:', os.path.sep, PATH )
        print(f'SCAN :: self.path = "{PATH}"')
        print(f'SCAN :: self.music_folder = "{MUSIC_FOLDER}"')
        self.music_folder   = MUSIC_FOLDER
        self.path           = PATH

    def handle(self, *args, **options):
        self.force          = options['force'] or False
        self.lyrics         = options['generatelyrics'] or False
        self.verbose        = options['verbose'] or False
        self.generator      = GenerateLyrics() if self.lyrics else None
        self.path           = ''
        self.music_folder   = ''
        self.language       = 'en'
        self.resolveBasePath(options["scan_path"][0])
        if self.force   : print("SCAN :: Enable Forced Analysis")
        if self.verbose : print("SCAN :: Enable High Verbosity")
        if self.lyrics  : 
            print("SCAN :: Enable Generate Lyrics using AI")
            self.generator.initialize('small')
        self.echo(f"SCAN :: Analyzed {len(self.scan( self.music_folder ))} songs.")
    
    def get_id3tags(self, filepath):
        """Devuelve un diccionario con los metadatos ID3 de un archivo MP3."""
        from mutagen.mp3 import MP3
        from mutagen.id3 import ID3    
        try:
            audio = MP3(filepath)
            tags =  ID3(filepath)
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
            print("SCAN :: ID3 Exception : "+str(e))
            return {
                "file": filepath,
                "error": str(e)
            }

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
        artist_name = artist_name.split('/')[0]
        artist_name = artist_name.split(',')[0]
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
                artist.save()
                if os.path.isdir(os.path.join(self.folder, '.artists')):
                    image_file = os.path.join(self.folder, '.artists', f'{sanitize(artist_name)}.jpg')
                    if os.path.isfile( image_file ):
                            with open(image_file, 'rb') as f:
                                artist.picture.save(os.path.basename(image_file), File(f), save=True)
                                artist.save()
                self.echo(f'+ Created artist "{ artist_name }"')
                return artist

    def get_or_create_genre(self, genre_name, info):
        if genre_name is None or len(genre_name.strip())==0: 
            return []
        genre_name.replace(" n ", '&')
        genre_name.replace("'n'", '&')
        genre_name.replace('and', '&')
        genre_name.replace(','  , '/')
        genres = genre_name.split('/')
        for genre_name in genres:
            genre_name = sanitize_name(genre_name)
            try:
                genre = Genre.objects.filter( name__iexact=genre_name ).get()
                return [genre]
            except Exception as e:
                genre = Genre()
                genre.name = genre_name
                genre.save()
                self.echo(f'+ Created genre "{ genre_name }"')
                return [genre]
                
    def get_or_create_tags(self, tags_text, song=None):
        if tags_text is None: return []
        tags_text=sanitize_name(tags_text)
        tags = []
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
                self.echo(f'+ Created tag "{tag_token}"')
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
            self.echo(f'+ Created album "{album_name}"')
            return album

    def add_song_error(self, song, exception, error=True):
        song.errors = song.errors + str(exception) + ';\n'
        if error:
            song.error = error

    def setup_title(self):
        try:
            self.song.title = self.info.get('title')
            if self.song.title is None:
                self.add_song_error(self.song, "Title not found. Using filename as fallback.")
                self.song.title = str(self.song.filename).split(PATH_SEP)[-1]
        except Exception as e:
            self.song.title = "Desconocido"
            self.add_song_error( self.song, f"TITLE:{str(e)}" )

    def setup_duration(self):
        try:
            self.song.duration = self.info.get('duration')
        except Exception as e:
            self.song.duration = 1
            self.add_song_error( self.song, f"DURATION:{str(e)}")
    
    def setup_trackno(self):
        value = self.info.get('track_number') or 0
        try:
            self.song.track_number = int(value.split('/')[0])
        except:            
            try:
                self.song.track_number = int(value)
            except Exception as e:            
                self.song.track_number = None
                self.add_song_error(self.song, f"TRACK:{str(e)}")

    def setup_timestamp(self):
        self.song.timestamp = None
        try:
            YEAR        = self.info.get('year') or "1000" # We use 1000 as 'special' value for discarding malformed timestamps
            TIMESTAMP   = datetime( int( sanitize_year( YEAR ) ), 1, 1)
            self.song.timestamp = timezone.make_aware( TIMESTAMP ) 
            if self.song.timestamp.year == 1000: 
                # Invalid Year, no audio from year 1000 could be recorded!
                self.song.timestamp = None
        except Exception as e:
            self.add_song_error(self.song, f"TIMESTAMP:{str(e)}")

    def setup_album(self):
        self.song.album = None
        try:
            self.song.album = self.get_or_create_album(self.info.get('album'), self.info)
        except Exception as e:
            self.add_song_error(self.song, f"ALBUM:{str(e)}")

    def setup_artist(self):
        self.song.artist = None
        try:
            self.song.artist = self.get_or_create_artist( self.info.get('artist'), self.info)
        except Exception as e:
            self.add_song_error(self.song, f"ARTIST:{str(e)}")
        try:
            if self.song.album:
                self.song.album.artists.add(self.song.artist)
                self.song.album.save()
        except Exception as e:
            self.add_song_error(self.song, f"ARTIST:{str(e)}")
        
    def setup_genre(self):
        self.song.genre = None
        try:
            genres = self.get_or_create_genre( self.info.get('genre'), self.info)
            for genre in genres:
                self.song.genres.add( genre )
                if self.song.album:
                    self.song.album.genres.add( genre )
                    self.song.album.save()
            if len(genres):
                self.song.genre = genres[0] 
        except Exception as e:
            self.add_song_error(self.song, f"GENRE:{str(e)}")

    def setup_bpm(self):
        self.song.bpm = None
        try:
            self.song.bpm = self.info.get('bpm') if is_number(self.info.get('bpm')) else None
        except Exception as e:
            self.add_song_error(self.song, f"BPM:{str(e)}")

    def setup_key(self):
        self.song.key = None
        try:
            self.song.key = self.info.get('key')
        except Exception as e:
            self.add_song_error(self.song, f"KEY:{str(e)}")

    def setup_picture(self):
        self.song.picture = None
        picture = self.info.get('picture')[0] if 'picture' in self.info.keys() else None
        if picture is not None:
            try:
                if self.song.picture == '':
                    sha = hashlib.sha512()
                    sha.update(picture)
                    filename = sha.hexdigest()  # 128 caracteres ASCII
                    path = os.path.join('.', "media", "songs", f'{filename}.png')
                    dump_picture(path, picture)
                    self.song.picture = f'/media/songs/{filename}.png'
            except Exception as e:
                self.add_song_error(self.song, f"PICTURE:{str(e)}")
            try:
                if self.song.album is not None:
                    if self.song.album.picture is None:
                        filename = sanitize_filename(self.song.album.name)
                        path = os.path.join('.', "media", "albums", f'{filename}.png')
                        dump_picture(path, picture)
                        self.song.album.picture = f'/media/albums/{filename}.png'
                        self.song.album.save()
            except Exception as e:
                self.add_song_error(self.song, f"PICTURE:{str(e)}")

    def setup_tags(self):
        self.song.comment = ''
        for tag in self.get_or_create_tags( self.info.get('comments'), self.song):
            try:
                self.song.tags.add(tag)
            except Exception as e:
                self.add_song_error(self.song, f"TAGS ({tag}): {str(e)}")
    
    def setup_lyrics(self):
        SRT_FILE = self.song.filename.rstrip('.mp3')+'.srt'
        self.song.lyrics = saferead(SRT_FILE) if os.path.exists(SRT_FILE) else ''
        try:
            self.song.lyrics = self.song.lyrics.replace('"', "'")
            if self.song.lyrics == '' and self.lyrics:
                self.echo(f"Generating Lyrics ({self.language})...")
                self.generator.work(self.song.filename, self.language)
                self.song.lyrics = saferead(SRT_FILE) if os.path.exists(SRT_FILE) else ''
        except Exception as e:
            self.add_song_error(self.song, f"LYRICS:{str(e)}")

    def setup_song(self):
        self.song.errors = ''
        self.song.error  = False
        self.song.hash   = self.hash
        self.setup_title()
        self.setup_duration()
        self.setup_trackno()
        self.setup_timestamp()
        self.setup_album()
        self.setup_artist()
        self.setup_bpm()
        self.setup_key()
        self.setup_picture()
        self.song.save()
        self.setup_genre()
        self.setup_tags()
        self.song.save()
        self.setup_lyrics()
        self.song.save()

    def update_song(self, filename : str):
        self.song = Song.objects.filter(filename=filename).get()
        self.setup_song()
        self.echo(f'· Updated song {filename}')

    def create_song(self, filename : str):
        self.song = Song()
        self.song.filename = filename
        self.setup_song()
        self.echo(f'· Created song "{filename}"')

    def scan(self, folder):        
        """Escanea una carpeta recursivamente en busca de archivos MP3."""
        results = []
        self.folder = folder
        for root, _, files in os.walk(folder):
            if is_ignored_path(root):
                continue
            self.tabs = "  " * len(root.split(folder)[1].split("\\"))
            last = root.split(folder)[1].split("\\")[-1]
            print(("  "*50)+"\r"+self.tabs+last.lstrip('\\').lstrip('/'))
            self.language = 'en'
            for f in files:
                if f.lower().endswith(".lang"):
                    self.language = f.strip('.lang')
                    continue
                if f.lower().endswith(".mp3"):
                    print(("  "*50)+"\r"+f, end="\r")
                    path        = os.path.join(root, f)
                    self.hash   = get_hash(path)
                    # check whether or not the song object exists
                    filename    = os.path.join(root, f)
                    song        = self.get_song(filename)
                    if (song is not None) and (song.hash == self.hash) and (not song.error) and (not (self.force or self.lyrics)):
                        continue
                    self.info = self.get_id3tags(path)
                    if song is None:
                        self.create_song( filename )
                    else:
                        self.update_song( filename )
                    if self.song and self.song.error and self.verbose:
                        for line in self.song.errors.replace('\n', '').split(';'):
                            if len(line)>0:
                                self.echo('/!\\ ' + line.strip('\n'))
                    results.append(self.info)
        return results

    