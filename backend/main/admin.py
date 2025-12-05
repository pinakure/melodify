from django.contrib import admin
from .models import Artist, Genre, Tag, Album, Song, Playlist


# ============
#   ARTIST
# ============
@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ("name", "aliases")
    search_fields = ("name", "aliases")
    filter_horizontal = ("genres",)
    #list_filter = ("genres",)


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
    filter_horizontal = ("artists", "genres")
    #list_filter = ("limited", "genres")


# ============
#   SONG
# ============
@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ("title", "artist", "album", "genre", "comment", "timestamp", "codename", "bpm", "all_tags", "favorite", "status")
    search_fields = ("title", "codename", "album__name")
    #list_filter = ("genre", "artist", "album", "bookmarked", "tags")
    
    def all_tags(self, obj):
        return obj.get_tags()

    @admin.display(boolean=True, description='✔')
    def status(self, obj):
        return not obj.error 
    
    @admin.display(boolean=False, description='💛')
    def favorite(self, obj):
        return "🤍" if not obj.bookmarked else "💛" 


# ============
#   PLAYLIST
# ============
@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ("title",)
    search_fields = ("title",)
    filter_horizontal = ("songs", "artists", "genres")

