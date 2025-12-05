from django.contrib import admin
from .models import Artist, Genre, Tag, Album, Song, Playlist


# ============
#   ARTIST
# ============
@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ("name", "aliases")
    search_fields = ("name", "aliases")
    list_filter = ("genres",)
    filter_horizontal = ("genres",)


# ============
#   GENRE
# ============
@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


# ============
#   TAG
# ============
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


# ============
#   ALBUM
# ============
@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ("name", "codename", "edition", "limited")
    search_fields = ("name", "codename")
    list_filter = ("limited", "genres")
    filter_horizontal = ("artists", "genres")


# ============
#   SONG
# ============
@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ("title", "artist", "album", "timestamp", "error")
    search_fields = ("title", "codename", "album__name")
    list_filter = ("genre", "artist", "album", "bookmarked", "tags")


# ============
#   PLAYLIST
# ============
@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ("title",)
    search_fields = ("title",)
    filter_horizontal = ("songs", "artists", "genres")

