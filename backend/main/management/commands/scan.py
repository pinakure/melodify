from django.core.management.base    import BaseCommand
from django.core.files              import File
from django.utils                   import timezone
from main.models                    import Song, Album, Artist, Tag, Genre
from main.utils                     import Utils, Sanitizer, debug
from datetime                       import datetime, timedelta
from .generatelyrics                import Command as GenerateLyrics
from .getartist                     import Command as GetArtist
import itertools
import platform
import hashlib
import os

class Command(BaseCommand):
    help = "Scans specified path looking for mp3 files to be scanned and added to the media library"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.verbose        = False
        self.tabs           = ''
        self.lyrics         = False 
        self.force          = False 
        self.generator      = GenerateLyrics() if self.lyrics else None
        self.path           = ''
        self.music_folder   = ''
        self.language       = 'en'

    def echo(self, text, end='\n'):
        try:
            debug(self.tabs+text, end=end)
            self.stdout.write("\r"+(" "*os.get_terminal_size().columns)+"\r"+self.tabs+text)
        except:
            debug(self.tabs+text, end=end)
            self.stdout.write(self.tabs+text)
    
    def add_arguments(self, parser):
        parser.add_argument("scan_path"                                 , nargs="+" , type=str  )
        parser.add_argument("--force"           , '-f', default=False   , nargs="*" , type=bool )
        parser.add_argument("--scrape"          , '-s', default=False   , nargs="*" , type=bool )
        parser.add_argument("--generatelyrics"  , '-g', default=False   , nargs="*" , type=bool )
        parser.add_argument("--verbose"         , '-V', default=False   , nargs="*" , type=bool )

    def resolveBasePath(self, BASEPATH):
        try:
            if platform.system() == 'Windows':
                os.system('cls')
            else:
                os.system('clear')
        except:
            pass
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
        self.echo(f'SCAN :: self.path = "{PATH}"')
        self.echo(f'SCAN :: self.music_folder = "{MUSIC_FOLDER}"')
        self.music_folder   = MUSIC_FOLDER
        self.path           = PATH

    def handle(self, *args, **options):
        self.echo(str(options.keys()))
        self.artistmetadata = GetArtist().initialize()
        self.scrape         = options['scrape'] or False
        self.force          = options['force'] or False
        self.lyrics         = options['generatelyrics'] or False
        self.verbose        = options['verbose'] or False
        self.resolveBasePath(options["scan_path"][0])
        if self.scrape  : self.echo("SCAN :: Scraping missing metadata")
        if self.force   : self.echo("SCAN :: Enable Forced Analysis")
        if self.verbose : self.echo("SCAN :: Enable High Verbosity")
        if self.lyrics  : self.echo("SCAN :: Enable Generate Lyrics using AI")
        self.echo(f"SCAN :: Analyzed {len(self.scan( self.music_folder , self.lyrics))} songs.")

    def add_song_error(self, song, exception, error=True):
        song.errors = song.errors + str(exception) + ';\n'
        if error:
            song.error = error
    
    def load_aliases(self):
        self.aliases = {}
        for root, _, files in os.walk( Utils.library_path('.artists') ):
            for file in files:
                if file.lower().endswith(".aka"):
                    artist = file.split( os.path.sep )[-1].rstrip('.aka').lower()
                    self.aliases[ artist ] = []
                    for alias in Utils.saferead(os.path.join(root, file), read_mode='r', encoding='utf-8').split('\n'):
                        self.aliases[ artist ].append( alias.lower() )

    def get_aliases(self, artist_name):
        query = artist_name.lower()
        for artist in self.aliases:
            if artist == query:
                payload = self.aliases[ artist ]
                # self.echo(f"! Aliases found for { artist_name }. Name has { len(payload)+1 } aliases.")
                payload.insert(0, artist )
                return payload
            for aliases in self.aliases:
                for alias in self.aliases[ aliases ]:
                    if query == alias.lower():
                        # self.echo(f"! Aliases found for artist '{ artist_name }'.")
                        # self.echo(f"  His true name is '{ artist.title() }'.")
                        payload = self.aliases[ artist ]
                        payload.insert(0, artist )
                        return payload
        return [ artist_name ] 

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
            self.echo("SCAN :: ID3 Exception : "+str(e))
            return {
                "file": filepath,
                "error": str(e)
            }

    def get_song(self, path : str):
        try:
            return Song.objects.filter(filename=path).get()
        except Exception:
            return None
   
    def get_song_by_hash(self, hash : str):
        try:
            return Song.objects.filter(hash=hash).get()
        except Exception:
            return None

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

    def get_or_create_artist(self, artist_name, aliases=[], type=''):
        if artist_name is None: return None
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
                artist.name     = artist_name.title()
                artist.aliases  = ','.join(aliases) if len(aliases) > 1 else ''
                artist.bio      = ''
                artist.picture = None
                artist.save()
                if os.path.isdir(Utils.library_path('.artists')):
                    image_file = Utils.library_path(os.path.join('.artists', f'{ Sanitizer.clean(artist_name.title()) }.jpg'))
                    if os.path.isfile( image_file ):
                            with open(image_file, 'rb') as f:
                                artist.picture.save(os.path.basename(image_file), File(f), save=True)
                                artist.save()
                self.artistmetadata.get_artist_metadata( artist_name )
                self.echo(f'+ Created { f"{type} " if type!="" else ""}artist "{ artist.name }"')
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
            genre_name = Sanitizer.name(genre_name)
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
        tags_text   = Sanitizer.name(tags_text)
        tags        = []
        tag_list    = tags_text.split(', ')
        res         = []
        [res.append(val) for val in tag_list if val not in res]
        tag_list = res
        for tag_token in tag_list:
            tag = None
            tag_token = Sanitizer.tag( tag_token, song )
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

    def setup_album(self):
        self.song.album = None
        try:
            self.song.album = self.get_or_create_album(self.info.get('album'), self.info)
        except Exception as e:
            self.add_song_error(self.song, f"ALBUM:{str(e)}")

    def setup_artist(self):
        self.song.artist = None
        try:
            artist_name = self.info.get('artist')
            class Payload:
                artists      = Sanitizer.artists( artist_name )
                artists_and  = Sanitizer.artists_and( artist_name )
                artists_feat = Sanitizer.artists_feat( artist_name )
                artists_vs   = Sanitizer.artists_vs( artist_name )
                artists_prod = Sanitizer.artists_prod( artist_name )
                aliases      = self.get_aliases( artists[0] )
            self.song.artist = self.get_or_create_artist( Payload.aliases[0], Payload.aliases)
            self.song.save()
            for _and    in Payload.artists_and  : self.song.artists_and.add ( self.get_or_create_artist( _and , type='coauthor') )
            for ft      in Payload.artists_feat : self.song.artists_feat.add( self.get_or_create_artist( ft   , type='featured') )
            for vs      in Payload.artists_vs   : self.song.artists_vs.add  ( self.get_or_create_artist( vs   , type='versus') )
            for prod    in Payload.artists_prod : self.song.artists_prod.add( self.get_or_create_artist( prod , type='producer') )
            self.song.save()
        except Exception as e:
            self.echo(str(e))
            self.add_song_error(self.song, f"ARTIST:{str(e)}")
        try:
            if self.song.album:
                self.song.album.artists.add(self.song.artist)
                for artist in itertools.chain( self.song.artists_and.all(), self.song.artists_feat.all(), self.song.artists_vs.all(), self.song.artists_prod.all()):
                    self.song.album.artists.add( artist )
                self.song.album.save()
        except Exception as e:
            self.echo(f"ERROR :: {str(e)}")
            self.add_song_error(self.song, f"ARTIST:{str(e)}")
    
    def setup_bpm(self):
        self.song.bpm = None
        try:
            self.song.bpm = self.info.get('bpm') if Utils.is_number(self.info.get('bpm')) else None
        except Exception as e:
            self.add_song_error(self.song, f"BPM:{str(e)}")   

    def setup_duration(self):
        try:
            self.song.duration = self.info.get('duration')
        except Exception as e:
            self.song.duration = 1
            self.add_song_error( self.song, f"DURATION:{str(e)}")

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

    def setup_key(self):
        self.song.key = None
        try:
            self.song.key = self.info.get('key')
        except Exception as e:
            self.add_song_error(self.song, f"KEY:{str(e)}")
    
    def setup_lyrics(self):
        SRT_FILE = self.song.filename.rstrip('.mp3')+'.srt'
        try:
            self.song.lyrics = Utils.saferead(SRT_FILE, 'r', encoding='utf-8') if os.path.exists(SRT_FILE) else ''
        except Exception as e:
            self.add_song_error(self.song, f"LYRICS:{str(e)}")
        try:
            self.song.lyrics = self.song.lyrics.replace('"', "'")
            if self.song.lyrics == '' and self.lyrics:
                self.echo(f"Generating Lyrics ({self.language})...")
                self.generator.work(self.song.filename, self.language, verbose=False, tabs=self.tabs)
                self.song.lyrics = Utils.saferead(SRT_FILE, 'r', encoding='utf-8') if os.path.exists(SRT_FILE) else ''
        except Exception as e:
            self.add_song_error(self.song, f"LYRICS:{str(e)}")

    def setup_karaoke(self):
        SRT_FILE = self.song.filename.rstrip('.mp3')+'.kar.srt'
        try:
            self.song.karaoke = Utils.saferead(SRT_FILE, 'r', encoding='utf-8') if os.path.exists(SRT_FILE) else ''
        except Exception as e:
            self.add_song_error(self.song, f"KARAOKE:{str(e)}")
    def setup_picture(self):
        from pathlib import Path
        self.song.picture = None
        picture = self.info.get('picture')[0] if 'picture' in self.info.keys() else None
        if picture is None:
            self.echo(f"SCAN :: No picture @ info, looking for '{ self.song.title }.png' in media/songs/")
            try:
                filename = Path(os.path.join('.', 'media', 'songs', f'{ self.song.title }.png'))
                if filename.exists():
                    self.echo(f"SCAN :: Picture found, reading picture data...")
                    picture = Utils.saferead(str(filename), 'rb')
            except Exception as e:
                self.echo(f"SCAN :: Failed to read '{ filename }'")
        
        if picture is not None:
            self.echo(f"SCAN :: Picture data is present, hashing image filename...")
            try:
                if self.song.picture is None:
                    sha = hashlib.sha512()
                    sha.update(picture)
                    filename = sha.hexdigest()  # 128 caracteres ASCII
                    path = os.path.join('.', "media", "songs", f'{filename}.png')
                    self.echo(f"SCAN :: Dumping Picture")
                    Utils.dump_picture(path, picture)
                    self.song.picture = f'/media/songs/{filename}.png'
                    self.echo(f"SCAN :: song.picture = '{ self.song.picture }'")
                    self.song.save()
                    self.echo(f"SCAN :: Song Picture Stored")
            except Exception as e:
                self.echo(f"SCAN :: Hashing Failed : {str(e)}")
                self.add_song_error(self.song, f"PICTURE:{str(e)}")
            try:
                if self.song.album is not None:
                    self.echo(f"SCAN :: Album picture is present, importing data")
                    if self.song.album.picture is None:
                        filename = Sanitizer.filename(self.song.album.name)
                        path = os.path.join('.', "media", "albums", f'{filename}.png')
                        Utils.dump_picture(path, picture)
                        self.song.album.picture = f'/media/albums/{filename}.png'
                        self.song.album.save()
            except Exception as e:
                self.echo(f"SCAN :: Album Picture import Failed : {str(e)}")
                self.add_song_error(self.song, f"PICTURE:{str(e)}")

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
        self.setup_karaoke()
        self.song.save()

    def setup_tags(self):
        self.song.comment = ''
        for tag in self.get_or_create_tags( self.info.get('comments'), self.song):
            try:
                self.song.tags.add(tag)
            except Exception as e:
                self.add_song_error(self.song, f"TAGS ({tag}): {str(e)}")

    def setup_title(self):
        try:
            self.song.title = self.info.get('title')
            if self.song.title is None:
                self.add_song_error(self.song, "Title not found. Using filename as fallback.")
                self.song.title = str(self.song.filename).split( os.path.sep )[-1]
        except Exception as e:
            self.song.title = "Desconocido"
            self.add_song_error( self.song, f"TITLE:{str(e)}" )

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
            TIMESTAMP   = datetime( int( Sanitizer.year( YEAR ) ), 1, 1)
            self.song.timestamp = timezone.make_aware( TIMESTAMP ) 
            if self.song.timestamp.year == 1000: 
                # Invalid Year, no audio from year 1000 could be recorded!
                self.song.timestamp = None
        except Exception as e:
            self.add_song_error(self.song, f"TIMESTAMP:{str(e)}")

    def create_song(self, filename : str):
        self.song = Song()
        self.song.filename = filename
        self.setup_song()
        self.echo(f'· Created song "{filename}"')

    def update_song(self, filename : str):
        self.song = Song.objects.filter(filename=filename).get()
        self.setup_song()
        self.echo(f'· Updated song {filename}')

    def scan(self, folder, generate_lyrics=False):        
        """Escanea una carpeta recursivamente en busca de archivos MP3."""
        results = []
        self.folder = folder
        if generate_lyrics:
            self.lyrics = generate_lyrics
            if self.generator is None:
                self.generator = GenerateLyrics() if self.lyrics else None
                self.generator.initialize('small')

        self.load_aliases()

        for root, _, files in os.walk(folder):
            if Utils.is_ignored_path(root):
                continue
            self.tabs = "  " * len(root.split(folder)[1].split("\\"))
            last = root.split(folder)[1].split("\\")[-1]
            self.echo(("  "*50)+"\r"+self.tabs+last.lstrip('\\').lstrip('/'))
            self.language = 'en'
            for f in files:
                if f.lower().endswith(".lang"):
                    self.language = f.strip('.lang')
            for f in files:
                if f.lower().endswith(".mp3"):
                    self.echo(("  "*50)+"\r"+f, end="\r")
                    path        = os.path.join(root, f)
                    self.hash   = Utils.get_hash(path)
                    # check whether or not the song object exists
                    filename    = os.path.join(root, f)
                    song        = self.get_song_by_hash(self.hash) #self.get_song(filename)
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

    