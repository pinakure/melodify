from django.core.management.base import BaseCommand
from main.models import Font
from main.utils import saferead
import os 

class Command(BaseCommand):
    help = "Imports fonts from /templates/fonts/ into the database"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        path = os.path.join('.', 'static', 'css')
        contents = saferead(os.path.join(path, 'fonts.css')).lstrip('\n').lstrip(':root {\n').lstrip('\n').rstrip('}').rstrip('\n').replace('\t', '').replace(';', '')
        fonts = contents.replace(' ', '').replace('\n\n', '').replace('\nurl', 'url').replace('@font-face{\n','').split('}')
        for font in fonts:    
            try:
                lines       = font.split('\n')
                fields      = { parts[0].strip().replace('--','') : parts[1].strip() for line in lines if ':' in line for parts in [line.split(':', 1)] }
                f = Font(
                    name        = fields['font-family'].strip("'"),
                    src         = fields['src'].replace('data:application/font-woff2charset=utf-8base64', 'data:application/font-woff2;charset=utf-8;base64'),
                    font_weight = fields['font-weight'].strip("'"),
                    font_style  = fields['font-style'].strip("'"),
                )
            except Exception as e:
                print(f"Bad format error : {e}")
                continue
            try:
                if Font.objects.filter(name=f.name).exists():
                    Font.objects.filter(name=f.name).delete()
                f.save()
                print(f"Imported Font {f.name}")
                continue
            except Exception as e:
                print(f"Database error : {e}")
                print(f"Skipping {f.name} import")
                continue