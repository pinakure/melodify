from django.contrib import admin
from django.urls import path
from main.views import *
from main import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path, include
from django.views.static import serve # Import the standard file server view


urlpatterns = [
    path('admin/'                   , admin.site.urls),
    path(''                         , LandingView.as_view()         , name='tag-list'),
    path('home'                     , HomeView.as_view()            , name='home'),
    path('accounts/'                , include('django.contrib.auth.urls')), # Línea clave para incluir las URLs de autenticación
    path('steal/'                   , StealView.as_view()           , name='steal'),
    path('stealget/'                , views.steal_get               , name='steal-get'),
    path('stealsearch/'             , views.steal_search            , name='steal-search'),
    path('player/'                  , PlayerView.as_view()          , name='player'),
    path('albums/'                  , AlbumTileView.as_view()       , name='album-tiles'),
    path('albums/<int:pk>/'         , AlbumDetailView.as_view()     , name='album-detail'),
    path('favorites/'               , FavoritesView.as_view()       , name='favorites'),
    path('genres/'                  , GenreListView.as_view()       , name='genre-list'),
    path('genre/<int:pk>/'          , GenreDetailView.as_view()     , name='genre-detail'),
    path('artists/'                 , ArtistListView.as_view()      , name='artist-list'),
    path('artist/<int:pk>/'         , ArtistDetailView.as_view()    , name='artist-detail'),
    path('playlists/'               , PlaylistListView.as_view()    , name='playlist-list'),
    path('playlists/new/'           , views.create_playlist_ajax    , name='create-playlist'),
    path('playlists/populate/'      , views.populate_playlist_ajax  , name='populate-playlist'),
    path('playlist/<int:pk>/'       , PlaylistDetailView.as_view()  , name='playlist-detail'),
    path('search/'                  , views.search_ajax             , name='search'),
    path('lyrics/<int:pk>/'         , LyricsView.as_view()          , name='lyrics'),
    path('lyrics/save/'             , views.save_lyrics_ajax        , name='save-lyrics'),
    path('tags/'                    , TagListView.as_view()         , name='tag-list'),
    path('settings/'                , SettingsView.as_view()        , name='settings'),
    path('scheme/<str:scheme>/'     , views.scheme_view_ajax        , name='scheme'),
    path('tag/<int:pk>/'            , TagDetailView.as_view()       , name='tag-detail'),
    path('song/<int:pk>/'           , SongDetailView.as_view()      , name='song-detail'),
    path('song/bookmark/'           , views.bookmark_song           , name='bookmark-song'),
    path('scan/artist/'             , views.scan_artist             , name='scan-artist'),
    path('play/<int:pk>/song.mp3'   , views.play_ajax               , name='play'),
    path('user/<int:pk>/'           , UserView.as_view()            , name='user'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    