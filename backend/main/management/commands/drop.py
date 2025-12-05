from django.core.management.base import BaseCommand
from main.models import Song, Album, Artist, Playlist, Tag, Genre

class Command(BaseCommand):
    help = "Drops Database"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        Song.objects.all().delete()
        Artist.objects.all().delete()
        Album.objects.all().delete()
        Playlist.objects.all().delete()
        Tag.objects.all().delete()
        Genre.objects.all().delete()