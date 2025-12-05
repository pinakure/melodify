from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Album, Song

class AlbumTileView(ListView):
    model = Album
    template_name = 'main/album-tiles.html'  # Ruta a tu nueva plantilla
    context_object_name = 'albums'           # Nombre de la variable en la plantilla

class AlbumDetailView(DetailView):
    model = Album
    template_name = 'main/album-detail.html' # Plantilla para el detalle
    context_object_name = 'album'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pipo'] = "popi"
        context['songs'] = Song.objects.filter(album=context['album'])
        return context
        