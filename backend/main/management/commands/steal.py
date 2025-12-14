from django.core.management.base import BaseCommand
from main.models import Song, Album, Artist, Playlist, Tag, Genre
from django.conf import settings
import shutil
from spotdl import Spotdl

import os 

"""
[
    Song(
        name='Carpe Diem', 
        artists=['Arce'], 
        artist='Arce', 
        genres=[], 
        disc_number=1, 
        disc_count=1, 
        album_name='Luciffer', 
        album_artist='Arce', 
        duration=256,
        year='2015', 
        date='2015-09-28', 
        track_number=1, 
        tracks_count=14, 
        song_id='3FNVEzMunpVrVda5nO7Kbs', 
        explicit=True, 
        publisher='Digital Hustlers',
        url='https://open.spotify.com/track/3FNVEzMunpVrVda5nO7Kbs', 
        isrc='ESA011510108',
        cover_url='https://i.scdn.co/image/ab67616d0000b273e8f1f29fd047f01ed2666b64', 
        copyright_text='2016 Arce', 
        download_url=None, 
        lyrics=None, 
        popularity=53,
        album_id='2u90rkPNOGOsbt2B1Lq9w8', 
        list_name='Luciffer', 
        list_url='https://open.spotify.com/album/2u90rkPNOGOsbt2B1Lq9w8', 
        list_position=None, 
        list_length=14,
        artist_id='7eH1UUCyxL8Wf9PztvvPJ6', 
        album_type='album'
    ), 
    Song(
    ...
    )
]
"""
spotdl = None

def clean(songname):
    songname = songname.replace('?', '')
    songname = songname.replace(':', '')
    songname = songname.replace('*', '')
    songname = songname.replace('/', '-')
    songname = songname.replace('\\', '')
    return songname

class Command(BaseCommand):
    help            = "Steal"
    initialized     = False
    spotdl          = None

    def initialize():
        Command.spotdl = Spotdl(
            client_id="dc75272b15354119b9df60392848cc6a", 
            client_secret="76d4dfef594f4625bd68b8068a574289", 
            no_cache=True
        )

    def add_arguments(self, parser):
        parser.add_argument("url", nargs="+", type=str)

    def searchSong(self, url):
        if not Command.initialized: Command.initialize()
        
        song_objs = Command.spotdl.search([url])
        payload = []
        for song in song_objs:
            payload.append({ 
                'name'   : song.name,
                'artist' : song.artist,
                'url'    : song.url,
                'album'  : song.album_name,
            }) 
        return payload
    
    def getSong(self, url):
        if not Command.initialized: Command.initialize()
                
        song_objs = Command.spotdl.search([url])
    
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
                dest     = os.path.join(settings.LIBRARY_ROOT, letter, artist, album, title)
                dstpath  = os.path.join(settings.LIBRARY_ROOT, letter, artist, album)
                if os.path.exists(os.path.join(dstpath,  title)):
                    print('Skipping download, song already exists.')
                    continue
                result   = Command.spotdl.download_songs([song])[0]
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
    
    def handle(self, *args, **options):
        URL = options["url"][0]
        print(("*"*80)+'\n'+f" Downloading {URL}..."+"\n"+("*"*80))
        self.getSong(URL);        
    