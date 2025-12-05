from django.contrib import admin
from django.urls import path
from main.views import AlbumTileView, AlbumDetailView, ArtistDetailView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('albums/', AlbumTileView.as_view(), name='album-tiles'),
    path('albums/<int:pk>/', AlbumDetailView.as_view(), name='album-detail'),
    path('artist/<int:pk>/', ArtistDetailView.as_view(), name='artist-detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
