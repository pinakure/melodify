from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Album, Song, Artist, Genre

def get_context( context ):
    # Enter global severside data here
    context['playlists'] = [
        { 
            'picture'   : '/media/songs/1bc2b164477f43b7e6a0894f3dcc807f42beaf5b5a5b2a4c0296db3e8eae0775e59d96f391439fcf03528875b59c57f1253ed99541fda6dcc08d1718a84dc91c.png',
            'primary'   : 'Canciones que te gustan',
            'secondary' : 'Lista · Smiker',
            'use_index' : False,
        },
        { 
            'picture'   : '/media/songs/1bc2b164477f43b7e6a0894f3dcc807f42beaf5b5a5b2a4c0296db3e8eae0775e59d96f391439fcf03528875b59c57f1253ed99541fda6dcc08d1718a84dc91c.png',
            'primary'   : 'Tus Episodios',
            'secondary' : 'Lista · Smiker',
            'use_index' : False,
        },
        { 
            'picture'   : '/media/songs/1bc2b164477f43b7e6a0894f3dcc807f42beaf5b5a5b2a4c0296db3e8eae0775e59d96f391439fcf03528875b59c57f1253ed99541fda6dcc08d1718a84dc91c.png',
            'primary'   : 'Me Gusta',
            'secondary' : 'Lista · Smiker',
            'use_index' : False,
        },
        { 
            'picture'   : '/media/songs/1bc2b164477f43b7e6a0894f3dcc807f42beaf5b5a5b2a4c0296db3e8eae0775e59d96f391439fcf03528875b59c57f1253ed99541fda6dcc08d1718a84dc91c.png',
            'primary'   : 'Blonde',
            'secondary' : 'Lista · Smiker',
            'use_index' : False,
        },
        { 
            'picture'   : '/media/songs/1bc2b164477f43b7e6a0894f3dcc807f42beaf5b5a5b2a4c0296db3e8eae0775e59d96f391439fcf03528875b59c57f1253ed99541fda6dcc08d1718a84dc91c.png',
            'primary'   : 'papa zen',
            'secondary' : 'Lista · Smiker',
            'use_index' : False,
        },
        { 
            'picture'   : '/media/songs/1bc2b164477f43b7e6a0894f3dcc807f42beaf5b5a5b2a4c0296db3e8eae0775e59d96f391439fcf03528875b59c57f1253ed99541fda6dcc08d1718a84dc91c.png',
            'primary'   : 'Terror para llevar',
            'secondary' : 'Lista · Smiker',
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
        obj = self.object
        return context

class AlbumDetailView(DetailView):
    model = Album
    template_name = 'main/album-detail.html'
    context_object_name = 'album'

    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs))
        album = self.object
        context['songs'] = Song.objects.filter(album=album)
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

class SongDetailView(DetailView):
    model = Song
    template_name = 'main/song-detail.html'
    context_object_name = 'song' 
    
    def get_context_data(self, **kwargs):
        context = get_context(super().get_context_data(**kwargs))
        obj = self.object
        return context