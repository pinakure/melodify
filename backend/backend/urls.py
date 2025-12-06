from django.contrib import admin
from django.urls import path
from main.views import AlbumTileView, AlbumDetailView, ArtistDetailView, ArtistListView, SongDetailView
from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path
from django.views.static import serve # Import the standard file server view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('albums/', AlbumTileView.as_view(), name='album-tiles'),
    path('albums/<int:pk>/', AlbumDetailView.as_view(), name='album-detail'),
    path('artists/', ArtistListView.as_view(), name='artist-list'),
    path('artist/<int:pk>/', ArtistDetailView.as_view(), name='artist-detail'),
    path('albums/<int:album_pk>/song/<int:pk>/', SongDetailView.as_view(), name='song-detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    