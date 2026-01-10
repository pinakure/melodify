from django.utils.decorators        import method_decorator
from django.views.decorators.csrf   import csrf_exempt
from main.management.commands.scan  import Command as Scan
from django.contrib.auth.models     import AnonymousUser
from django.contrib.auth.forms      import AuthenticationForm
from django.core.paginator          import Paginator, EmptyPage, PageNotAnInteger
from django.forms.models            import model_to_dict
from django.views.generic           import ListView, DetailView, TemplateView, View
from django.contrib.auth            import authenticate, login, logout, get_user_model
from django.db.models               import Case, When, Count, Value, Min
from django.db.models               import Q
from django.utils.html              import mark_safe
from django.http                    import JsonResponse, HttpResponse
from django.conf                    import settings            
from main.models                    import *
from main.utils                     import Utils, debug
import subprocess
import json
import os

scanner = Scan()

def get_context( context , user):
    # Enter global severside data here
    context['playlists'] = Playlist.objects.all()
    sidebar = [
        { 
            'picture'   : '/static/images/like.png',
            'primary'   : 'Favoritos',
            'secondary' : 'Lista',
            'url'       : 'favorites',
            'use_index' : False,
        },
    ]
    for playlist in context['playlists']:
        sidebar.append({
            'picture'   : playlist.picture.url if playlist.picture.name else None,  
            'primary'   : playlist.title,
            'secondary' : playlist.get_artists(),
            'url'       : f'playlist/{playlist.id}',
            'use_index' : False,
        })
    context['sidebar'] = sidebar
    context['playlists'] = get_playlists(user)
    context['favorites'] = get_favorites(user)
    context['analyzer_range'] = range(32)
    context['version'] = settings.VERSION
    return context
    
def get_favorites(user):
    if user.is_authenticated:
        return Song.objects.filter(bookmark__usuario=user).distinct().annotate(fav=Value(True)) 
    else:  
        return []

def get_playlists(user):
    if user.is_authenticated:
        return Playlist.objects.filter(usuario=user)
    else:  
        return []
    
# returns song object with virtual 'fav' field embedded, tuned for given user_id
def get_song(song_id, user_id):
    song =  Song.objects.filter(id = song_id).annotate(fav=Exists(Bookmark.objects.filter(song_id=OuterRef('pk'),usuario_id=user_id))).get()
    song.pretty_artist = mark_safe(song.pretty_artist()) 
    song.artist_count  = song.get_artist_count() 
    return song


class AlbumTileView(ListView):
    model = Album
    template_name = 'main/album-tiles.html' 
    context_object_name = 'albums'          
    paginate_by = 32  

    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs), self.request.user)
        return context

    def get_queryset(self):
        queryset = Album.objects.order_by('name')       

        # Obtenemos el término de búsqueda de los parámetros GET (para peticiones AJAX y normales)
        search_query = self.request.GET.get('search', None)

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | 
                Q(artists__name__icontains=search_query)
            ).distinct() # Usamos distinct si la búsqueda en M2M duplica resultados

        return queryset

    def get(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Petición AJAX: devolvemos JSON
            page = request.GET.get('page', 1)
            queryset = self.get_queryset() # Usamos el queryset ya filtrado por `get_queryset`
            paginator = Paginator(queryset, self.paginate_by)
            
            try:
                items = paginator.page(page)
            except (PageNotAnInteger, EmptyPage):
                return JsonResponse({'albums': []})

            data = []
            for item in items:
                data.append({
                    'id'            : item.id,
                    'nombre'        : item.name,
                    'artist'        : item.get_artists(),
                    'safeartist'    : item.get_artists().lower(),
                    'safename'      : item.name.lower(),
                    'descripcion'   : item.brief,
                    'url_picture'   : f'{item.picture}',
                    'url_detalle'   : f'/albums/{item.id}/',
                })
            return JsonResponse({'albums': data, 'total_count': queryset.count()})
        return super().get(request, *args, **kwargs)
from django.db.models import Exists, OuterRef

class AlbumDetailView(DetailView):
    model = Album
    template_name = 'main/album-detail.html'
    context_object_name = 'album'

    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs), self.request.user)
        album = self.object
        context['songs'] = Song.objects.filter(album=album).annotate(fav=Exists(Bookmark.objects.filter(song_id=OuterRef('pk'),usuario_id=self.request.user.pk))).order_by('track_number')
        return context

class ArtistListView(ListView):
    model = Artist
    template_name = 'main/artist-list.html'  
    context_object_name = 'artists'         
    queryset = Artist.objects.order_by('picture') 
    # queryset = Artist.objects.order_by('name') 

    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs), self.request.user)
        context['albums_list'] = Album.objects.all().order_by('-release')
        return context
    
class ArtistDetailView(DetailView):
    model = Artist
    template_name = 'main/artist-detail.html'
    context_object_name = 'artist' 

    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs), self.request.user)
        artist = self.object
        context['songs'] = Song.objects.filter(Q(artist=artist) | Q(artists_and__name__icontains=artist)| Q(artists_feat__name__icontains=artist)| Q(artists_vs__name__icontains=artist)| Q(artists_prod__name__icontains=artist)).annotate(fav=Exists(Bookmark.objects.filter(song_id=OuterRef('pk'),usuario_id=self.request.user.pk)))
        context['albums_list'] = Album.objects.filter(artists__pk=artist.id).all().order_by('-release')
        return context
    
class GenreListView(ListView):
    model = Genre
    template_name = 'main/genre-list.html'  
    context_object_name = 'genres'         
    queryset = Genre.objects.order_by('name') 

    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs), self.request.user)
        return context

class GenreDetailView(DetailView):
    model = Genre
    template_name = 'main/genre-detail.html'
    context_object_name = 'genre' 
    
    def get_context_data(self, **kwargs):
        genre = self.object
        context = get_context(super().get_context_data(**kwargs), self.request.user)
        context['songs'] = Song.objects.filter(genre=genre).annotate(fav=Exists(Bookmark.objects.filter(song_id=OuterRef('pk'),usuario_id=self.request.user.pk))).order_by('track_number')
        context['albums_list'] = Album.objects.filter(genres__pk=genre.id).all().order_by('-release')
        return context

class TagListView(ListView):
    model = Tag
    template_name = 'main/tag-list.html'  
    context_object_name = 'tags'         
    queryset = Tag.objects.order_by('name') 

    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs), self.request.user)
        return context
    
class StealView(ListView):
    model = Song
    template_name = 'main/steal.html'  
    context_object_name = 'songs'         
    queryset = Song.objects.order_by('title') 

    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs), self.request.user)
        return context
    
class FavoritesView(ListView):
    model = Playlist
    template_name = 'main/favorites.html'  
    context_object_name = 'songs'
    queryset = None
    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs), self.request.user)
        context['songs'] = context['favorites']
        return context

class PlayerView(TemplateView):
    template_name = 'main/full-player.html'  

    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs), self.request.user)
        song_id = self.request.GET.get('song')
        if song_id is None:
            return context        
        context['song']     = get_song( song_id, self.request.user.pk)
        context['artist']   = context['song'].artist
        return context

class ManagementView(TemplateView):
    template_name = 'main/management.html'  

    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs), self.request.user)
        context['log'] = Utils.saferead(settings.LOG_FILE, 'r', encoding='utf-8')
        return context

class LandingView(TemplateView):
    template_name = 'main/landing.html' 
    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs), self.request.user)
        return context

class HomeView(TemplateView):
    template_name = 'main/home.html'  
    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs), self.request.user)
        context['songs'] = Song.objects.order_by('?').annotate(fav=Exists(Bookmark.objects.filter(song_id=OuterRef('pk'),usuario_id=self.request.user.pk)))[:25]
        return context

class SettingsView(TemplateView):
    template_name = 'main/settings.html'  
    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs), self.request.user)
        context['schemes'               ] = Scheme.objects.all().order_by('name').values('name')
        context['fonts'                 ] = Font.objects.all().order_by('name').values('name')
        context['scheme_data'           ] = Scheme.objects.all().order_by('name').values()
        context['library_root'          ] = Utils.library_path()
        context['spotify_client_id'     ] = settings.SPOTIFY_CLIENT_ID
        context['spotify_client_secret' ] = settings.SPOTIFY_CLIENT_SECRET
        return context
    
class LyricsView(DetailView):
    model = Song
    template_name = 'main/lyrics.html'  
    context_object_name = 'song' 
    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs), self.request.user)
        return context

class UserView(ListView):
    model = Song
    template_name = 'main/home.html'  
    context_object_name = 'songs'         
    queryset = Song.objects.order_by('?')[:25]

    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs), self.request.user)
        return context

class TagDetailView(DetailView):
    model = Tag
    template_name = 'main/tag-detail.html'
    context_object_name = 'tag' 
    
    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs), self.request.user)
        tag = self.object
        context['songs'] = Song.objects.filter(tags__pk=tag.id).annotate(fav=Exists(Bookmark.objects.filter(song_id=OuterRef('pk'),usuario_id=self.request.user.pk))).order_by('track_number')
        return context

class PlaylistListView(TemplateView):
    template_name = 'main/playlist-tiles.html'  
    paginate_by = 32  

    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs), self.request.user)
        return context

    def get_queryset(self, user_id):
        queryset = Playlist.objects.filter(usuario__id=user_id).order_by('title') 
    
        # Obtenemos el término de búsqueda de los parámetros GET (para peticiones AJAX y normales)
        search_query = self.request.GET.get('search', None)

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) #| 
                #Q(artists__name__icontains=search_query)|
                #Q(songs__name__icontains=search_query)
                # Q(genres__name__icontains=search_query)
            ).distinct() # Usamos distinct si la búsqueda en M2M duplica resultados

        return queryset

    def get(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Petición AJAX: devolvemos JSON
            page    = request.GET.get('page', 1)
            user_id = request.GET.get('user_id', 0)
            queryset = self.get_queryset(user_id) # Usamos el queryset ya filtrado por `get_queryset`
            paginator = Paginator(queryset, self.paginate_by)
            
            try:
                items = paginator.page(page)
            except (PageNotAnInteger, EmptyPage):
                return JsonResponse({'playlists': []})

            data = []
            for item in items:
                data.append({
                    'id'            : item.id,
                    'nombre'        : item.title,
                    'artists'       : item.get_artists(),
                    'safeartist'    : item.get_artists().lower(),
                    'genres'        : item.get_genres(),
                    'safename'      : item.title.lower(),
                    'url_picture'   : f'{item.picture}',
                    'url_detalle'   : f'/playlist/{item.id}/',
                })
            return JsonResponse({'playlists': data, 'total_count': queryset.count()})
        return super().get(request, *args, **kwargs)
        return JsonResponse({'playlists': [], 'total_count': 0})


class PlaylistDetailView(DetailView):
    model = Playlist
    template_name = 'main/playlist-detail.html'
    context_object_name = 'playlist' 
    
    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs), self.request.user)
        playlist = self.object
        context['songs'] = playlist.songs.all().annotate(fav=Exists(Bookmark.objects.filter(song_id=OuterRef('pk'),usuario_id=self.request.user.pk)))
        context['back'] = self.request.GET.get('back', '')
        # context['albums_list'] = Album.objects.filter(artists__pk=artist.id).all().order_by('-release')
        
        return context
    
class SongDetailView(DetailView):
    model = Song
    template_name = 'main/song-detail.html'
    context_object_name = 'song' 
    
    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs), self.request.user)
        context['song'] = get_song( context['song'].pk, self.request.user.pk)
        return context
      
class UserView(DetailView):
    model = get_user_model()
    template_name = 'main/user.html'
    context_object_name = 'user' 
    
    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs), self.request.user)
        context['playlists' ] = Playlist.objects.filter(usuario__id=self.request.user.id)
        context['authed'    ] = True if self.request.user.is_authenticated else False

        return context

@csrf_exempt
def scheme_view_ajax(request, scheme):
    obj = model_to_dict(Scheme.objects.filter(name=scheme).get())
    css_vars = {f"--{k.replace('_', '-')}": v.replace('"', '') for k, v in obj.items()}
    return JsonResponse({'status': 'success', 'scheme': scheme, 'values' : css_vars})
    
@csrf_exempt
def search_ajax(request):
    if request.content_type == 'application/json':
        data = json.loads(request.body)
        topic = data.get('topic', '')
    else:
        topic = request.POST.get('topic', '')
    results = {
        'albums' : list(
            Album.objects.filter(name__icontains=topic)
            .annotate(artist_count=Count('artists', distinct=True)) # Importante el distinct=True aquí
            .annotate(
                artist__name=Case(
                    When(artist_count__gt=1, then=Value('Varios Artistas')),
                    # Min('artists__name') agrupa todos los nombres y elige uno solo (el primero alfabéticamente)
                    default=Min('artists__name'), 
                )
            )
            .values('id', 'name', 'picture', 'artist__name')
            .distinct()[:50]
        ),
        'artists' : list(Artist.objects.filter(name__icontains=topic     )[:50].values('id', 'name'  , 'picture')),
        'songs'   : list(Song.objects.filter(title__icontains=topic      )[:50].values('id', 'title' , 'picture', 'artist__name')),
        'lists'   : list(Playlist.objects.filter(title__icontains=topic  )[:50].values('id', 'title' , 'picture')),
        'genres'  : list(Genre.objects.filter(name__icontains=topic      )[:50].values('id', 'name'  )),
        'tags'    : list(Tag.objects.filter(name__icontains=topic        )[:50].values('id', 'name'  )),
        'users'   : [],
    }
    return JsonResponse({'status': 'success', 'results': results })

def create_playlist_ajax(request):
    if isinstance(request.user , AnonymousUser):
        return JsonResponse({ 'status' : 'login'})
    if request.method == 'POST':
        try:
            # Leer los datos JSON del cuerpo de la petición
            data = json.loads(request.body)
            playlist_name = data.get('name', '').strip()
            
            if not playlist_name:
                return JsonResponse({'status': 'error', 'message': 'El nombre no puede estar vacío.'}, status=400)

            new_playlist = Playlist.objects.create(
                title=playlist_name,
                usuario=request.user # 
            )
            
            return JsonResponse({'status': 'success', 'message': 'Playlist creada', 'id': new_playlist.id})

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'JSON inválido'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    # Si alguien intenta acceder por GET a esta URL, lo ignoramos o redirigimos
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=445)

def save_lyrics_ajax(request):
    if isinstance(request.user , AnonymousUser):
        return JsonResponse({ 'status' : 'login'})
    if request.method == 'POST':
        try:
            # Leer los datos JSON del cuerpo de la petición
            data = json.loads(request.body)
            song = data.get('song', '').strip()
            lyrics = data.get('lyrics', '').strip()
            
            if not song:
                return JsonResponse({'status': 'error', 'message': 'Missing Song'}, status=400)
            if not lyrics:
                return JsonResponse({'status': 'error', 'message': 'Missing Lyrics'}, status=400)

            song = Song.objects.filter(id=song).get()
            song.lyrics = lyrics
            song.save()            
            return JsonResponse({'status': 'success', 'message': 'Letras actualizadas.'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'JSON inválido'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    # Si alguien intenta acceder por GET a esta URL, lo ignoramos o redirigimos
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=445)

def play_ajax(request, pk):
    # if isinstance(request.user , AnonymousUser):
    #     return JsonResponse({ 'status' : 'login'})
    if request.method == 'GET':
        try:
            # Leer los datos JSON del cuerpo de la petición
            song = pk
            
            if not song:
                return JsonResponse({'status': 'error', 'message': 'Missing Song'}, status=400)

            # get song binary data from file 
            song = Song.objects.filter(id=pk).get()
            data = Utils.saferead(song.filename, 'rb')
            response = HttpResponse(data, content_type='application/octet-stream')
            # response['Content-Disposition'] = 'attachment; filename="archivo.bin"'
            return response
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'JSON inválido'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    # Si alguien intenta acceder por GET a esta URL, lo ignoramos o redirigimos
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=445)

def steal_get(request):
    if isinstance(request.user , AnonymousUser):
        return JsonResponse({ 'status' : 'login'})
    if request.method == 'POST':
        try:
            # Leer los datos JSON del cuerpo de la petición
            data = json.loads(request.body)
            url = data.get('url', '').strip()
            
            if not url:
                return JsonResponse({'status': 'error', 'message': 'url no puede estar vacío.'}, status=400)
            args = [ 'python', os.path.join('scripts', 'steal.py'), url]
            debug(f"STEAL :: args = {args}")
            result = subprocess.run(
                args,
                capture_output=True, 
                timeout=3600,
                text=True
            )
            songs = result.stdout.replace("'''", '').replace('\n', '').replace("'", '"')
            debug(f"STEAL :: stderr = {result.stderr}")
            debug(f"STEAL :: result = {result.stdout}")
            debug(f"STEAL :: songs = {songs}")
            return JsonResponse({'status': 'success', 'message': 'Steal OK', 'songs' : json.loads(songs)})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'JSON inválido'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    # Si alguien intenta acceder por GET a esta URL, lo ignoramos o redirigimos
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=445)

def steal_search(request):
    if isinstance(request.user , AnonymousUser):
        return JsonResponse({ 'status' : 'login'})
    if request.method == 'POST':
        try:
            # Leer los datos JSON del cuerpo de la petición
            data = json.loads(request.body)
            url = data.get('url', '').strip()
            
            if not url:
                return JsonResponse({'status': 'error', 'message': 'url no puede estar vacío.'}, status=400)

            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
            args = [ 'python', os.path.join('scripts', 'steal.py'), url, '--search_only']
            try:
                debug(f"STEAL :: args = {args}")
                env = os.environ.copy()
                env["PYTHONIOENCODING"] = 'utf-8'
                env["LANG"] = 'en_US.UTF-8'
                os.environ["PATH"] += os.pathsep + "/usr/bin"
                env["PATH"]+=os.pathsep + "/usr/bin"
                result = subprocess.run(
                    args,
                    capture_output=True, 
                    text=True
                )
                debug(f"STEALSEARCH :: result = '{result}'")
                debug(f"STEALSEARCH :: stdout = '{result.stdout}'")
                songs = result.stdout.replace("'''", '').replace('\n', '').replace("'", '"')
                debug(f"STEALSEARCH :: songs = '{songs}'")
                debug(f"STEALSEARCH :: stderr = '{result.stderr}'")
                return JsonResponse({'status': 'success', 'message': 'Search OK', 'songs' : json.loads(songs)})
            except Exception as e:
                debug(f"STEALSEARCH :: Exception : {str(e)}")
                return JsonResponse({'status': 'error', 'message': str(e)})

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'JSON inválido'}, status=400)
        # except Exception as e:
            # return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    # Si alguien intenta acceder por GET a esta URL, lo ignoramos o redirigimos
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=445)

def scan_artist(request):
    if isinstance(request.user , AnonymousUser):
        return JsonResponse({ 'status' : 'login'})
    LIBRARY_ROOT = Utils.library_path()
    if request.method == 'POST':
        try:
            # Leer los datos JSON del cuerpo de la petición
            data = json.loads(request.body)
            artist = data.get('artist', '').strip()
            lyrics = bool(data.get('generate_lyrics', ''))
            if not artist:
                return JsonResponse({'status': 'error', 'message': 'artist no puede estar vacío.'}, status=400)
            songs = scanner.scan(os.path.join(LIBRARY_ROOT, artist[0].upper(), artist), lyrics)
            return JsonResponse({'status': 'success', 'message': 'Scan OK', 'songs' : songs})

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'JSON inválido'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    # Si alguien intenta acceder por GET a esta URL, lo ignoramos o redirigimos
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=445)

def bookmark_song(request):
    if isinstance(request.user , AnonymousUser):
        return JsonResponse({ 'status' : 'login'})
    
    if request.method == 'POST':
        try:
            # Leer los datos JSON del cuerpo de la petición
            data    = json.loads(request.body)
            song_id = data.get('song', '').strip()
            
            if not song_id:
                return JsonResponse({'status': 'error', 'message': 'Debe especificarse un ID.'}, status=400)

            try:
                bookmark = Bookmark.objects.filter(usuario=request.user, song__id=song_id).get()
                if bookmark: 
                    bookmark.delete()
                    return JsonResponse({'status': 'success', 'message': 'Eliminada de Favoritos', 'id': song_id})
            except:
                bookmark = Bookmark()
                bookmark.usuario  = request.user
                bookmark.song_id = song_id
                bookmark.save()
                return JsonResponse({'status': 'success', 'message': 'Agregada a Favoritos', 'id': song_id})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'JSON inválido'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    # Si alguien intenta acceder por GET a esta URL, lo ignoramos o redirigimos
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=445)

def populate_playlist_ajax(request):
    if isinstance(request.user , AnonymousUser):
        return JsonResponse({ 'status' : 'login'})
    if request.method == 'POST':
        try:
            # Leer los datos JSON del cuerpo de la petición
            data = json.loads(request.body)
            playlist_id = int(data.get('playlist', '').strip())
            song_id     = int(data.get('song', '').strip())
            
            if not playlist_id or not song_id:
                return JsonResponse({'status': 'error', 'message': 'Debeb especificarse lista y pista.'}, status=400)

            playlist = Playlist.objects.filter(id=playlist_id).get()
            playlist.songs.add(Song.objects.filter(id=song_id).get())
            playlist.save()
            return JsonResponse({'status': 'success', 'message': 'Pista añadida a lista.', 'id': playlist_id})

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'JSON inválido'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    # Si alguien intenta acceder por GET a esta URL, lo ignoramos o redirigimos
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=445)

@csrf_exempt    
def log_ajax(request):
    from datetime import datetime
    if request.user.is_superuser and request.content_type == 'application/json':
        data  = json.loads(request.body)
        clear = data.get('clear', False)
        if clear: 
            CRLF = '\n'
            Utils.safewrite(settings.LOG_FILE, f'{"-"*80}{CRLF}Log clearing requested by { request.user.username } @ { datetime.now().strftime('%a %H:%M  %d/%m/%y') }{CRLF}{"-"*80}{CRLF}')        
        return JsonResponse({"status" : 'success', "response": "\n".join(Utils.saferead(settings.LOG_FILE, 'r', encoding='utf-8').split('\n')[-4096:])})
    else:
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=445)

@csrf_exempt    
def admin_ajax(request):
    if request.user.is_superuser and request.content_type == 'application/json':
        data   = json.loads(request.body)
        action = data.get('action', False)
        ACTIONS = {
            'db-export'     : Utils.db_export,
            'db-import'     : Utils.db_import,
            'db-drop'       : Utils.db_drop,
            'library-scan'  : Utils.library_scan,
            'library-lyrics': Utils.library_lyrics,
            'library-scrape': Utils.library_scrape,
        }
        if action in ACTIONS.keys():
            response = ACTIONS[ action ]()
        else: response = "Unknown Action"
        return JsonResponse({"status" : 'success', "response": response })
    else:
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=445)

def login_ajax(request):
    if request.method == 'POST':
        # Handle nostr authentication
        try:
            data = json.loads(request.body)
            signed_event = data.get('event')
            debug(f"NOSTR :: signed_event = {signed_event is not None}")
            if signed_event:
                debug(f"NOSTR :: Authenticating user")
                user = authenticate(request, signed_event_json=signed_event)
                debug(f"NOSTR :: user = '{user}'")
                if user:
                    debug(f"NOSTR :: Logging in {user}")
                    login(request, user)
                    return JsonResponse({"status": "ok", "method": "nostr"})
        except Exception as e:
            debug(f'NOST :: Exception : {str(e)}')
        
        # Handle traditional authentication    
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

def logout_ajax(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Método no permitido'}, status=405)