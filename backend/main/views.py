from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.db.models       import Q
from .models import Album, Song, Artist, Genre, Playlist, Tag

def get_context( context ):
    # Enter global severside data here
    context['playlists'] = [
        { 
            'picture'   : '/media/songs/1bc2b164477f43b7e6a0894f3dcc807f42beaf5b5a5b2a4c0296db3e8eae0775e59d96f391439fcf03528875b59c57f1253ed99541fda6dcc08d1718a84dc91c.png',
            'primary'   : 'Me Gusta',
            'secondary' : 'Lista ⌬ Smiker Pinakure Mageek',
            'use_index' : False,
        },
        { 
            'picture'   : '/media/songs/1bc2b164477f43b7e6a0894f3dcc807f42beaf5b5a5b2a4c0296db3e8eae0775e59d96f391439fcf03528875b59c57f1253ed99541fda6dcc08d1718a84dc91c.png',
            'primary'   : 'Blonde',
            'secondary' : 'Album ⌬ Frank Ocean',
            'use_index' : False,
        },
        { 
            'picture'   : '/media/songs/1bc2b164477f43b7e6a0894f3dcc807f42beaf5b5a5b2a4c0296db3e8eae0775e59d96f391439fcf03528875b59c57f1253ed99541fda6dcc08d1718a84dc91c.png',
            'primary'   : 'papa zen',
            'secondary' : 'Artista',
            'use_index' : False,
        },
        { 
            'picture'   : '/media/songs/1bc2b164477f43b7e6a0894f3dcc807f42beaf5b5a5b2a4c0296db3e8eae0775e59d96f391439fcf03528875b59c57f1253ed99541fda6dcc08d1718a84dc91c.png',
            'primary'   : 'Terror para llevar',
            'secondary' : 'Podcast ⌬ YoSoyPride',
            'use_index' : False,
        },
        { 
            'picture'   : '/media/songs/1bc2b164477f43b7e6a0894f3dcc807f42beaf5b5a5b2a4c0296db3e8eae0775e59d96f391439fcf03528875b59c57f1253ed99541fda6dcc08d1718a84dc91c.png',
            'primary'   : 'Canciones que te gustan',
            'secondary' : 'Lista ⌬ 119 canciones',
            'use_index' : False,
        },
        { 
            'picture'   : '/media/songs/1bc2b164477f43b7e6a0894f3dcc807f42beaf5b5a5b2a4c0296db3e8eae0775e59d96f391439fcf03528875b59c57f1253ed99541fda6dcc08d1718a84dc91c.png',
            'primary'   : 'Tus Episodios',
            'secondary' : 'Lista ⌬ Episodios guardados y descargados',
            'use_index' : False,
        },
        { 
            'picture'   : '/media/songs/1bc2b164477f43b7e6a0894f3dcc807f42beaf5b5a5b2a4c0296db3e8eae0775e59d96f391439fcf03528875b59c57f1253ed99541fda6dcc08d1718a84dc91c.png',
            'primary'   : 'Me Gusta',
            'secondary' : 'Lista ⌬ Smiker Pinakure Mageek',
            'use_index' : False,
        },
        { 
            'picture'   : '/media/songs/1bc2b164477f43b7e6a0894f3dcc807f42beaf5b5a5b2a4c0296db3e8eae0775e59d96f391439fcf03528875b59c57f1253ed99541fda6dcc08d1718a84dc91c.png',
            'primary'   : 'Blonde',
            'secondary' : 'Album ⌬ Frank Ocean',
            'use_index' : False,
        },
        { 
            'picture'   : '/media/songs/1bc2b164477f43b7e6a0894f3dcc807f42beaf5b5a5b2a4c0296db3e8eae0775e59d96f391439fcf03528875b59c57f1253ed99541fda6dcc08d1718a84dc91c.png',
            'primary'   : 'papa zen',
            'secondary' : 'Artista',
            'use_index' : False,
        },
        { 
            'picture'   : '/media/songs/1bc2b164477f43b7e6a0894f3dcc807f42beaf5b5a5b2a4c0296db3e8eae0775e59d96f391439fcf03528875b59c57f1253ed99541fda6dcc08d1718a84dc91c.png',
            'primary'   : 'Terror para llevar',
            'secondary' : 'Podcast ⌬ YoSoyPride',
            'use_index' : False,
        },
        { 
            'picture'   : '/media/songs/1bc2b164477f43b7e6a0894f3dcc807f42beaf5b5a5b2a4c0296db3e8eae0775e59d96f391439fcf03528875b59c57f1253ed99541fda6dcc08d1718a84dc91c.png',
            'primary'   : 'Canciones que te gustan',
            'secondary' : 'Lista ⌬ 119 canciones',
            'use_index' : False,
        },
        { 
            'picture'   : '/media/songs/1bc2b164477f43b7e6a0894f3dcc807f42beaf5b5a5b2a4c0296db3e8eae0775e59d96f391439fcf03528875b59c57f1253ed99541fda6dcc08d1718a84dc91c.png',
            'primary'   : 'Tus Episodios',
            'secondary' : 'Lista ⌬ Episodios guardados y descargados',
            'use_index' : False,
        },
    ]
    return context

class AlbumTileView(ListView):
    
    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs))
        return context
    
class AlbumTileView(ListView):
    model = Album
    template_name = 'main/album-tiles.html' 
    context_object_name = 'albums'          
    paginate_by = 32  

    def get_context_data(self, **kwargs):
        # Asegúrate de que tu función get_context maneje correctamente el contexto
        context = get_context(super().get_context_data(**kwargs))
        return context

    # Modificamos get_queryset para centralizar la lógica de filtrado/ordenación
    def get_queryset(self):
        # Definimos el queryset base
        queryset = Album.objects.order_by('name')
        
        # Obtenemos el término de búsqueda de los parámetros GET (para peticiones AJAX y normales)
        search_query = self.request.GET.get('search', None)

        if search_query:
            # Filtramos por nombre de álbum O nombre de artista usando Q objects
            # get_artists() es un método de tu modelo que asumo que existe.
            # Nota: Filtrar por métodos personalizados puede ser ineficiente a escala. 
            # Una mejor práctica sería buscar en un campo M2M indexado si es posible.
            
            # Esto es un ejemplo básico de cómo buscar:
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
                    'id': item.id,
                    'nombre': item.name,
                    'artist': item.get_artists(),
                    'safeartist': item.get_artists().lower(),
                    'safename': item.name.lower(),
                    'descripcion': item.brief,
                    'url_picture': f'{item.picture}',
                    'url_detalle': f'/albums/{item.id}/',
                })
            return JsonResponse({'albums': data, 'total_count': queryset.count()})
        
        # Petición normal: renderiza la vista HTML completa (incluye la primera página filtrada si hay búsqueda)
        return super().get(request, *args, **kwargs)

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
    # queryset = Artist.objects.order_by('-picture') 
    queryset = Artist.objects.order_by('name') 

    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs))
        context['albums_list'] = Album.objects.all().order_by('-release')
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

class SongDetailView(DetailView):
    model = Song
    template_name = 'main/song-detail.html'
    context_object_name = 'song' 
    
    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs))
        obj = self.object
        return context
    
class TagListView(ListView):
    model = Tag
    template_name = 'main/tag-list.html'  
    context_object_name = 'tags'         
    queryset = Tag.objects.order_by('name') 

    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs))
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
    template_name = 'main/playlist-list.html'  
    context_object_name = 'playlists'         
    queryset = Playlist.objects.order_by('title') 

    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs))
        return context

class PlaylistDetailView(DetailView):
    model = Playlist
    template_name = 'main/playlist-detail.html'
    context_object_name = 'playlist' 
    
    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs))
        # playlist = self.object
        return context