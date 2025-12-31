from django.core.management.base import BaseCommand
from main.models import Scheme
from main.utils import saferead
import os 

class Command(BaseCommand):
    help = "Imports schemes from /templates/schemes/ into the database"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        path = os.path.join('.', 'templates', 'schemes')
        print(f"Looking for scheme files in {path}")
        for scheme_file in [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]:
            scheme_name = scheme_file.split('.')[0]
            print(f"Processing {scheme_name}")
            contents    = saferead(os.path.join(path, scheme_file)).lstrip('\n').lstrip(':root {\n').lstrip('\n').rstrip('}').rstrip('\n').replace('\t', '').replace(';', '')
            lines       = contents.split('\n')
            try:
                fields      = { parts[0].strip().replace('--','').replace('-', '_'): parts[1].strip() for line in lines if ':' in line for parts in [line.split(':', 1)] }
            except Exception as e:
                print(f"Bad format error : {e}")
                print(f"Skipping {scheme_file} import")
                continue
            if Scheme.objects.filter(name=scheme_name).exists():
                  Scheme.objects.filter(name=scheme_name).delete()
            scheme = Scheme(**fields)
            scheme.name = scheme_name
            scheme.save()
            continue