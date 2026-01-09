from django.core.management.base import BaseCommand
from main.models import Song, Album, Artist, Playlist, Tag, Genre
from django.conf import settings
import os 

def empty(folder):
    for root, dirs, files in os.walk(os.path.join(settings.MEDIA_ROOT, folder)):
        for file in files:
            os.remove(os.path.join(settings.MEDIA_ROOT,folder, file))


class Command(BaseCommand):
    help = "Drops Database"

    def add_arguments(self, parser):
        pass

    def run(self):
        Song.objects.all().delete()
        Artist.objects.all().delete()
        Album.objects.all().delete()
        Playlist.objects.all().delete()
        Tag.objects.all().delete()
        Genre.objects.all().delete()
        empty('artists')
        empty('albums')
        empty('songs')

    def handle(self, *args, **options):
        self.run()