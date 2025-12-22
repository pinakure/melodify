from django.shortcuts import render
from django.views.generic import ListView, DetailView, TemplateView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Case, When, Count, Value, F, Subquery, Min, Max
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import redirect
from django.db.models import Q
import sys
import subprocess
from io import StringIO
from django.core.management import execute_from_command_line
import os
from django.conf import settings            
from main.management.commands.scan  import Command as Scan

import json
from .models import Album, Song, Artist, Genre, Playlist, Tag

scanner = Scan()

def get_context( context ):
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
    return context

class AlbumTileView(ListView):
    model = Album
    template_name = 'main/album-tiles.html' 
    context_object_name = 'albums'          
    paginate_by = 32  

    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs))
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

class AlbumDetailView(DetailView):
    model = Album
    template_name = 'main/album-detail.html'
    context_object_name = 'album'

    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs))
        album = self.object
        context['songs'] = Song.objects.filter(album=album).order_by('track_number')
        return context

class ArtistListView(ListView):
    model = Artist
    template_name = 'main/artist-list.html'  
    context_object_name = 'artists'         
    queryset = Artist.objects.order_by('picture') 
    # queryset = Artist.objects.order_by('name') 

    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs))
        context['albums_list'] = Album.objects.all().order_by('-release')
        return context
    
class ArtistDetailView(DetailView):
    model = Artist
    template_name = 'main/artist-detail.html'
    context_object_name = 'artist' 

    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs))
        artist = self.object
        context['songs'] = Song.objects.filter(artist=artist)
        context['albums_list'] = Album.objects.filter(artists__pk=artist.id).all().order_by('-release')
        return context
    
class GenreListView(ListView):
    model = Genre
    template_name = 'main/genre-list.html'  
    context_object_name = 'genres'         
    queryset = Genre.objects.order_by('name') 

    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs))
        return context

class GenreDetailView(DetailView):
    model = Genre
    template_name = 'main/genre-detail.html'
    context_object_name = 'genre' 
    
    def get_context_data(self, **kwargs):
        genre = self.object
        context = get_context(super().get_context_data(**kwargs))
        context['songs'] = Song.objects.filter(genre=genre).order_by('track_number')
        context['albums_list'] = Album.objects.filter(genres__pk=genre.id).all().order_by('-release')
        return context

class TagListView(ListView):
    model = Tag
    template_name = 'main/tag-list.html'  
    context_object_name = 'tags'         
    queryset = Tag.objects.order_by('name') 

    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs))
        return context
    
class StealView(ListView):
    model = Song
    template_name = 'main/steal.html'  
    context_object_name = 'songs'         
    queryset = Song.objects.order_by('title') 

    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs))
        return context
    
class FavoritesView(ListView):
    model = Playlist
    template_name = 'main/favorites.html'  
    context_object_name = 'songs'
    queryset = Song.objects.filter(bookmarked=True)

    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs))
        return context

class PlayerView(TemplateView):
    template_name = 'main/full-player.html'  

    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs))
        song_id = self.request.GET.get('song')
        print("SONG ID-------------------------------")
        print(song_id)
        if song_id is None:
            return context
        song    = Song.objects.filter(id=song_id).get()
        context['song']     = song
        context['artist']   = song.artist
        return context

class LandingView(ListView):
    model = Playlist
    template_name = 'main/landing.html'  
    context_object_name = 'playlists'         
    queryset = Playlist.objects.all()

    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs))
        context['favorites'] = Song.objects.filter(bookmarked=True)
        return context

class HomeView(ListView):
    model = Song
    template_name = 'main/home.html'  
    context_object_name = 'songs'         
    queryset = Song.objects.order_by('?')[:25]

    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs))
        context['favorites'] = Song.objects.filter(bookmarked=True)
        context['playlists'] = Playlist.objects.all()
        return context

class SettingsView(TemplateView):
    template_name = 'main/settings.html'  
    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs))
        return context
    
class LyricsView(TemplateView):
    template_name = 'main/lyrics.html'  
    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs))
        return context

class UserView(ListView):
    model = Song
    template_name = 'main/home.html'  
    context_object_name = 'songs'         
    queryset = Song.objects.order_by('?')[:25]

    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs))
        context['favorites'] = Song.objects.filter(bookmarked=True)
        context['playlists'] = Playlist.objects.all()
        return context

class TagDetailView(DetailView):
    model = Tag
    template_name = 'main/tag-detail.html'
    context_object_name = 'tag' 
    
    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs))
        tag = self.object
        context['songs'] = Song.objects.filter(tags__pk=tag.id).order_by('track_number')
        #context['albums_list'] = Album.objects.filter(genres__pk=tag.id).all().order_by('-release')
        return context

class PlaylistListView(ListView):
    model = Playlist
    template_name = 'main/playlist-tiles.html'  
    context_object_name = 'playlists'         
    paginate_by = 32  

    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs))
        return context

    def get_queryset(self):
        queryset = Playlist.objects.order_by('title') 
    
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
            page = request.GET.get('page', 1)
            queryset = self.get_queryset() # Usamos el queryset ya filtrado por `get_queryset`
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

class PlaylistDetailView(DetailView):
    model = Playlist
    template_name = 'main/playlist-detail.html'
    context_object_name = 'playlist' 
    
    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs))
        playlist = self.object
        context['songs'] = playlist.songs.all()
        context['back'] = self.request.GET.get('back', '')
        # context['albums_list'] = Album.objects.filter(artists__pk=artist.id).all().order_by('-release')
        
        return context
    
class SongDetailView(DetailView):
    model = Song
    template_name = 'main/song-detail.html'
    context_object_name = 'song' 
    
    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs))
        obj = self.object
        return context
    
@csrf_exempt
def scheme_view_ajax(request, scheme):
    scheme = scheme.strip('.')
    with open(f'templates/schemes/{ scheme }.css', 'r') as f:
        values = f.read()
    return JsonResponse({'status': 'success', 'scheme': scheme, 'values' : values})
    
@csrf_exempt
def search_ajax(request):
    if request.content_type == 'application/json':
        data = json.loads(request.body)
        topic = data.get('topic', '')
    else:
        topic = request.POST.get('topic', '')
    print("*"*80)
    print(f"  Searching term {topic} ")
    print("*"*80)
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
            result = subprocess.run(
                args,
                capture_output=True, 
                text=True
            )
            songs = result.stdout.replace("'''", '').replace('\n', '').replace("'", '"')
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
                result = subprocess.run(
                    args,
                    capture_output=True, 
                    text=True
                )
                songs = result.stdout.replace("'''", '').replace('\n', '').replace("'", '"')
                return JsonResponse({'status': 'success', 'message': 'Search OK', 'songs' : json.loads(songs)})
            except Exception as e:
                print(str(e))
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
    if request.method == 'POST':
        try:
            # Leer los datos JSON del cuerpo de la petición
            data = json.loads(request.body)
            artist = data.get('artist', '').strip()
            
            if not artist:
                return JsonResponse({'status': 'error', 'message': 'artist no puede estar vacío.'}, status=400)
            songs = scanner.scan(os.path.join(settings.LIBRARY_ROOT, artist[0].upper(), artist), False)
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

            song = Song.objects.filter(id=song_id).get()
            song.bookmarked = song.bookmarked ^ 1
            song.save()
            if song.bookmarked: 
                return JsonResponse({'status': 'success', 'message': 'Agregada a Favoritos', 'id': song_id})
            else:
                return JsonResponse({'status': 'success', 'message': 'Eliminada de Favoritos', 'id': song_id})

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