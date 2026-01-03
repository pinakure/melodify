from django.core.management.base    import BaseCommand
from django.conf                    import settings
from main.utils                     import Utils
from django.core.files              import File
from main.models                    import Artist
import requests
import os 

class Command(BaseCommand):
    help = "Scraps Artist metadata from Spotify"

    def add_arguments(self, parser):
        parser.add_argument("artist" , nargs="+" , type=str  )

    def get_artist_metadata(self, nombre_artista):
        print(f"SCRAP-ARTIST :: Searching metadata : { nombre_artista }", end="\r")
        filename  = f'{ nombre_artista }.jpg'
        dst_filename = Utils.library_path(os.path.join('.artists', filename.replace('"', '')))
        if os.path.exists(dst_filename):
            return
         
        resultados = self.sp.search(q='artist:' + nombre_artista, type='artist', limit=1)
        items = resultados['artists']['items']
        
        print((" "*100), end="\r")
        if len(items) > 0:
            artista = items[0]
            # Spotify devuelve una lista de imágenes en diferentes tamaños
            # La primera ([0]) suele ser la de mayor resolución (ej. 640x640)
            try:
                url_imagen = artista['images'][0]['url']
                print(f"SCRAP-ARTIST ::      Picture found : {url_imagen}")
                respuesta = requests.get(url_imagen)
                Utils.safewrite( dst_filename, respuesta.content, binary=True)
                print(f"SCRAP-ARTIST :: Picture downloaded : {dst_filename}.")
                artist = Artist.objects.filter(name=nombre_artista).get()
                if os.path.isfile( dst_filename ):
                    with open(dst_filename, 'rb') as f:
                        artist.picture.save(os.path.basename(dst_filename), File(f), save=True)
                        artist.save()
            except Exception as e:
                print(f"SCRAP-ARTIST ::  Picture not found : { nombre_artista }")
        else:
            print(f"SCRAP-ARTIST ::   Artist not found : { nombre_artista }")

    def initialize(self):
        import spotipy
        from spotipy.oauth2 import SpotifyClientCredentials
        self.auth_manager = SpotifyClientCredentials(client_id=settings.SPOTIFY_CLIENT_ID, client_secret=settings.SPOTIFY_CLIENT_SECRET)
        self.sp = spotipy.Spotify(auth_manager=self.auth_manager)
        return self

    def handle(self, *args, **options):
        self.initialize()
        artist = options['artist'][0]
        if artist == "*":
            for artist in Artist.objects.all():
                self.get_artist_metadata( artist.name )
        else:
            self.get_artist_metadata( artist )



