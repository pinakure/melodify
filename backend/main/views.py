from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Album, Song, Artist, Genre

class AlbumTileView(ListView):
    model = Album
    template_name = 'main/album-tiles.html' 
    context_object_name = 'albums'          

class AlbumDetailView(DetailView):
    model = Album
    template_name = 'main/album-detail.html'
    context_object_name = 'album'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        album = self.object
        context['songs'] = Song.objects.filter(album=album)
        return context

class ArtistDetailView(DetailView):
    model = Artist
    template_name = 'main/artist-detail.html'
    context_object_name = 'artist' 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)        
        artist = self.object
        context['songs'] = Song.objects.filter(artist=artist)
        context['albums_list'] = Album.objects.filter(artists__pk=artist.id).all().order_by('-release')
        return context

class SongDetailView(DetailView):
    model = Song
    template_name = 'main/song-detail.html'
    context_object_name = 'song' 