from django.db import models


# ============
#   ARTIST
# ============
class Artist(models.Model):
    name = models.CharField(max_length=200)
    aliases = models.CharField(max_length=300, blank=True)
    bio = models.TextField(blank=True)
    picture = models.ImageField(upload_to="artists/", blank=True, null=True)
    genres = models.ManyToManyField("Genre", blank=True)

    def __str__(self):
        return self.name


# ============
#   GENRE
# ============
class Genre(models.Model):
    name = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.name


# ============
#   TAG
# ============
class Tag(models.Model):
    name = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.name


# ============
#   ALBUM
# ============
class Album(models.Model):
    name    = models.CharField(max_length=200)
    codename= models.CharField(max_length=200, unique=True, null=True, blank=True)
    brief   = models.TextField(blank=True)
    picture = models.ImageField(upload_to="albums/", blank=True, null=True)
    booklet = models.FileField(upload_to="booklets/", blank=True, null=True)
    edition = models.CharField(max_length=200, blank=True, default="Vanila")
    limited = models.BooleanField(default=False)

    artists = models.ManyToManyField(Artist, blank=True)
    genres  = models.ManyToManyField(Genre, blank=True)

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
    filename     = models.FileField(upload_to="songs/")
    artist       = models.ForeignKey(Artist, on_delete=models.SET_NULL, null=True, blank=True)
    genre        = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True)
    comment      = models.TextField(blank=True)
    
    track_number = models.PositiveIntegerField(default=1, null=True, blank=True)
    lyrics       = models.TextField(blank=True)
    picture      = models.ImageField(upload_to="songs/", blank=True, null=True)

    times_played = models.PositiveIntegerField(default=0)
    times_skipped= models.PositiveIntegerField(default=0)
    bookmarked   = models.BooleanField(default=False)

    album        = models.ForeignKey(Album, on_delete=models.SET_NULL, null=True, blank=True)
    codename     = models.CharField(max_length=200, blank=True)

    tags         = models.ManyToManyField(Tag, blank=True)

    error        = models.BooleanField(default=False)
    errors       = models.TextField(blank=True, null=True)

    timestamp    = models.DateTimeField(null=True, blank=True)
    hash         = models.CharField(max_length=128, blank=True)
    bpm          = models.FloatField(null=True, blank=True)
    tone         = models.CharField(max_length=50, blank=True)

    def get_tags(self):
        tags = [ x.name for x in self.tags.all()]
        return ", ".join(tags)

    def __str__(self):
        return self.title


# ============
#   PLAYLIST
# ============
class Playlist(models.Model):
    title = models.CharField(max_length=200)
    songs = models.ManyToManyField(Song, blank=True)
    artists = models.ManyToManyField(Artist, blank=True)
    picture = models.ImageField(upload_to="playlists/", blank=True, null=True)
    genres = models.ManyToManyField(Genre, blank=True)

    def __str__(self):
        return self.title

