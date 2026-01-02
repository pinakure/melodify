from django.contrib import admin
from django.utils.html import format_html
from .models import Artist, Genre, Tag, Album, Song, Playlist, Scheme, Font


# ============
#   SCHEMES
# ============
@admin.register(Scheme)
class SchemeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

# ============
#   FONTS
# ============
@admin.register(Font)
class FontAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

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
    list_display = ("name", "artist", "genre", "songs", "codename", "pic", "book", "edition", "ltd")
    search_fields = ("name", "codename")
    filter_horizontal = ("artists", "genres")
    #list_filter = ("limited", "genres")

    def artist(self, obj):
        return format_html('<div style="width: 250px;">{}</div>', obj.get_artists())
    
    def songs(self, obj):
        return Song.objects.filter(album=obj).count()
    
    def genre(self, obj):
        return format_html('<div style="width: 250px;">{}</div>', obj.get_genres())
    
    def pic(self, obj):
        return "" if obj.picture is None else "✔"
     
    def book(self, obj):
        return "✔" if obj.booklet.name != "" else ""
    
    def ltd(self, obj):
        return "✔" if obj.limited else ""

# ============
#   SONG
# ============
@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ("title", "artist", "album", "genre", "comment", "year", "codename", "bpm", "all_tags", "status")
    search_fields = ("title", "codename", "album__name")
    #list_filter = ("genre", "artist", "album", "bookmarked", "tags")
    
    def all_tags(self, obj):
        return obj.get_tags()
    
    def year(self, obj):
        return obj.timestamp.strftime('%Y') if obj.timestamp else " "
    
    @admin.display(boolean=True, description='✔')
    def status(self, obj):
        return not obj.error 
    

# ============
#   PLAYLIST
# ============
@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ("title",)
    search_fields = ("title",)
    filter_horizontal = ("songs", "artists", "genres")

