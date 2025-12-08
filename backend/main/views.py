from django.shortcuts import render
from django.views.generic import ListView, DetailView
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
    model = Album
    template_name = 'main/album-tiles.html' 
    context_object_name = 'albums'          
    
    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs))
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
        # tag= self.object
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