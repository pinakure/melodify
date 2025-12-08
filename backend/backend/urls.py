from django.contrib import admin
from django.urls import path
from main.views import *
from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path
from django.views.static import serve # Import the standard file server view


urlpatterns = [
    path('admin/'               , admin.site.urls),
    path('albums/'              , AlbumTileView.as_view()       , name='album-tiles'),
    path('albums/<int:pk>/'     , AlbumDetailView.as_view()     , name='album-detail'),
    path('genres/'              , GenreListView.as_view()       , name='genre-list'),
    path('artists/'             , ArtistListView.as_view()      , name='artist-list'),
    path('tags/'                , TagListView.as_view()         , name='tag-list'),
    path('playlists/'           , PlaylistListView.as_view()    , name='playlist-list'),
    path('artist/<int:pk>/'     , ArtistDetailView.as_view()    , name='artist-detail'),
    path('song/<int:pk>/'       , SongDetailView.as_view()      , name='song-detail'),
    path('playlist/<int:pk>/'   , PlaylistDetailView.as_view()  , name='playlist-detail'),
    path('genre/<int:pk>/'      , GenreDetailView.as_view()     , name='genre-detail'),
    path('tag/<int:pk>/'        , TagDetailView.as_view()       , name='tag-detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    