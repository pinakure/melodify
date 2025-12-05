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
        context['pipo'] = "popi"
        context['songs'] = Song.objects.filter(album=context['album'])
        return context

class ArtistDetailView(DetailView):
    model = Artist
    template_name = 'main/artist-detail.html'
    context_object_name = 'artist' 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        current_artist = self.object

        # Añadir todos los álbumes de este artista al contexto, ordenados por fecha
        context['albums_list'] = current_artist.albums.all().order_by('-release_date')
        
        # Si tienes un modelo de Canciones relacionado con Álbumes, puedes iterar por ellos en la plantilla
        # context['all_songs'] = Song.objects.filter(album__artists=current_artist)

        return context
