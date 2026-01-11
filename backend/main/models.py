from django.db          import models
from django.conf        import settings
from django.utils.html  import mark_safe
# ============
#   ARTIST
# ============
class Artist(models.Model):
    name        = models.CharField(max_length=200)
    aliases     = models.CharField(max_length=300, blank=True)
    bio         = models.TextField(blank=True)
    picture     = models.ImageField(upload_to="artists/", blank=True, null=True)
    genres      = models.ManyToManyField("Genre", blank=True)

    def __str__(self):
        return self.name
    
# ============
#   GENRE
# ============
class Genre(models.Model):
    name        = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True, default="")

    def __str__(self):
        return self.name

# ============
#   TAG
# ============
class Tag(models.Model):
    name        = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.name

# ============
#   ALBUM
# ============
class Album(models.Model):
    name        = models.CharField(max_length=200)
    codename    = models.CharField(max_length=200, unique=True, null=True, blank=True)
    brief       = models.TextField(blank=True)
    picture     = models.CharField(max_length=512, default="", null=True, blank=True)
    booklet     = models.FileField(upload_to="booklets/", blank=True, null=True)
    edition     = models.CharField(max_length=200, blank=True, default="Vanila")
    limited     = models.BooleanField(default=False)
    release     = models.DateField(null=True, blank=True)

    artists     = models.ManyToManyField(Artist, blank=True)
    genres      = models.ManyToManyField(Genre, blank=True)

    def get_artists(self):
        artists = [ x.name for x in self.artists.all()]
        return ", ".join(artists)

    def get_genres(self):
        genres = [ x.name for x in self.genres.all()]
        return ", ".join(genres)

    def __str__(self):
        return self.name

# ============
#   SONG
# ============
class Song(models.Model):
    title        = models.CharField(max_length=200, default="Untitled")
    filename     = models.CharField(max_length=255, default="untitled.mp3")
    
    artist       = models.ForeignKey(Artist, on_delete=models.SET_NULL, null=True, blank=True)
    artists_and  = models.ManyToManyField(Artist, blank=True, related_name="artists_and")
    artists_feat = models.ManyToManyField(Artist, blank=True, related_name="artists_feat")
    artists_vs   = models.ManyToManyField(Artist, blank=True, related_name="artists_vs")
    artists_prod = models.ManyToManyField(Artist, blank=True, related_name="artists_prod")
    
    genre        = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True, related_name="genre")
    genres       = models.ManyToManyField(Genre, blank=True, related_name="genres")
    comment      = models.TextField(blank=True)
    
    track_number = models.PositiveIntegerField(default=1, null=True, blank=True)
    lyrics       = models.TextField(blank=True)
    karaoke      = models.TextField(blank=True)
    picture      = models.CharField(max_length=512, default="", null=True, blank=True)

    times_played = models.PositiveIntegerField(default=0)
    times_skipped= models.PositiveIntegerField(default=0)

    album        = models.ForeignKey(Album, on_delete=models.SET_NULL, null=True, blank=True)
    codename     = models.CharField(max_length=200, blank=True)

    tags         = models.ManyToManyField(Tag, blank=True)

    error        = models.BooleanField(default=False)
    errors       = models.TextField(blank=True, null=True)
    duration     = models.DurationField(default=1, null=True, blank=True)
    public       = models.BooleanField(default=False)
    timestamp    = models.DateTimeField(null=True, blank=True)
    hash         = models.CharField(max_length=128, blank=True)
    bpm          = models.FloatField(null=True, blank=True)
    tone         = models.CharField(max_length=50, blank=True)

    def get_tags(self):
        tags = [ x.name for x in self.tags.all()]
        return ", ".join(tags)
    
    def get_artist_count(self):
        count =  self.artists_and.all().count()
        count += self.artists_feat.all().count()
        count += self.artists_vs.all().count()
        count += self.artists_prod.all().count()
        return count+1
      
    def pretty_artist(self):
        if self.artist is None: return None
        def artist_link(artist):
            return f'<a onclick="melodify.navigate(`/artist/{ artist.pk }/`)">{ artist.name }</a>'
        artist = artist_link(self.artist)
        artist += " & " if len(self.artists_and.all())>0 else ''
        artist += ", ".join([ artist_link(x) for x in self.artists_and.all()])
        artist += " Ft. " if len(self.artists_feat.all())>0 else ''
        artist += ", ".join([ artist_link(x) for x in self.artists_feat.all()])
        artist += " Vs " if len(self.artists_vs.all())>0 else ''
        artist += ", ".join([ artist_link(x) for x in self.artists_vs.all()])
        artist += " Produced By " if len(self.artists_prod.all())>0 else ''
        artist += ", ".join([ artist_link(x) for x in self.artists_prod.all()])
        return artist

    def __str__(self):
        return self.title
    

# ============
#   PLAYLIST
# ============
class Playlist(models.Model):
    title   = models.CharField(max_length=200)
    songs   = models.ManyToManyField(Song, blank=True)
    artists = models.ManyToManyField(Artist, blank=True)
    picture = models.ImageField(upload_to="playlists/", blank=True, null=True)
    genres  = models.ManyToManyField(Genre, blank=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def get_artists(self):
        artists = [ x.name for x in self.artists.all()]
        return ", ".join(artists)

    def get_genres(self):
        genres = [ x.name for x in self.genres.all()]
        return ", ".join(genres)

    def __str__(self):
        return self.title


# ============
#   BOOKMARKS
# ============
class Bookmark(models.Model):
    song    = models.ForeignKey(Song, on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f'{ self.usuario.username } {self.song.title}'


# ===========
# SCHEMES 
# ===========
class Scheme(models.Model):
    from main.utils import Utils
    name                 = models.CharField(primary_key=True, max_length =    128, default = 'default'            )
    bg_main              = models.CharField(max_length =    128, default = '#0A0A0A'          )
    bg_nav               = models.CharField(max_length =    128, default = '#121212'          )
    bg_sidebar           = models.CharField(max_length =    128, default = '#1A1A1A'          )
    bg_sidebar_selection = models.CharField(max_length =    128, default = '#333333'          )
    bg_sidebar_hover     = models.CharField(max_length =    128, default = '#222222'          )
    bg_content_blend     = models.CharField(max_length =    128, default = '#0A0A0AC0'        )
    bg_content           = models.CharField(max_length =    128, default = '#0f0f0f'          )
    text_color           = models.CharField(max_length =    128, default = '#ffffff'          )
    link_color           = models.CharField(max_length =    128, default = '#cccccc'          )
    accent_color         = models.CharField(max_length =    128, default = '#ffa340'          )
    secondary_color      = models.CharField(max_length =    128, default = '#888888'          )
    section_color        = models.CharField(max_length =    128, default = '#eeeeee'          )
    confirm_color        = models.CharField(max_length =    128, default = '#dddddd'          )
    bg_player_title      = models.CharField(max_length =    128, default = '#2a2a2a'          )
    shadow_color         = models.CharField(max_length =    128, default = '#000000'          )
    tile_placeholder     = models.CharField(max_length =    128, default = '#333333'          )
    tile_info            = models.CharField(max_length =    128, default = '#050505'          )
    tile_info_text       = models.CharField(max_length =    128, default = '#666666'          )
    gradient_begin       = models.CharField(max_length =    128, default = '#444444'          )
    gradient_end         = models.CharField(max_length =    128, default = '#111111'          )
    nav_height           = models.CharField(max_length =     32, default = '60px'               )
    sidebar_width        = models.CharField(max_length =     32, default = '432px'              )
    default_font         = models.CharField(max_length =     32, default = "'lunchtype-regular'")
    player_font          = models.CharField(max_length =     32, default = "'lunchtype-regular'")
    player_font_size     = models.CharField(max_length =     32, default = '24px'               )
    renderer             = models.CharField(max_length =     32, default = 'themed'             )
    library_path         = models.CharField(max_length =    256, default = Utils.library_path() )

# ===========
# FONTS 
# ===========
class Font(models.Model):
    name                = models.CharField(primary_key=True, max_length = 32, default = 'default')
    font_weight         = models.CharField(max_length=10, default = 'normal',blank=True)
    font_style          = models.CharField(max_length=32, default = 'normal',blank=True)
    src                 = models.TextField(blank=False, null=False)
      
# ===========
# NOSTR LOGIN 
# ===========
class NostrProfile(models.Model):
    user                = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='nostr_profile')
    pubkey              = models.CharField(max_length=64, unique=True, help_text="Public key en formato hex")

    def __str__(self):
        return f"{self.user.username} - {self.pubkey[:8]}"
    
# ============
# FRIEND MODEL 
# ============
class Friend(models.Model):
    user                = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='friend_user')
    friend              = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='friend_friend')
    since               = models.DateField(auto_now_add=True)

# ==========
# STAT MODEL 
# ==========
class Interaction(models.Model):
    user                = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='songstat_user')
    song                = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='songstat_song')
    listens             = models.IntegerField(default=0)
    shares              = models.IntegerField(default=0)

MODELS = {
    'Artist'        : Artist,
    'Genre'         : Genre,
    'Tag'           : Tag,
    'Album'         : Album, 
    'Song'          : Song, 
    'Playlist'      : Playlist, 
    'Bookmark'      : Bookmark, 
    'Scheme'        : Scheme, 
    'Font'          : Font, 
    'NostrProfile'  : NostrProfile, 
    'Friend'        : Friend, 
    'Interaction'   : Interaction,
}