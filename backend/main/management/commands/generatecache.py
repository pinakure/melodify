from django.core.management.base import BaseCommand
from main.models import Font
from main.utils import safewrite
import os 

class Command(BaseCommand):
    help = "(Re)generates fonts CSS cache file"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        contents = ''
        fonts = Font.objects.all()
        for font in fonts:
            contents += "@font-face { \n"
            contents += '\t'+f"font-family: '{font.name         }';"+'\n'
            contents += '\t'+f"font-weight: '{font.font_weight  }';"+'\n'
            contents += '\t'+f"font-style : '{font.font_style   }';"+'\n'
            contents += '\t'+f"src        :  {font.src          };"+'\n'
            contents += '}\n'
        path = os.path.join('.', 'static', 'css')
        size = safewrite(os.path.join(path, 'fonts.css'), contents)
        print(f"Regenerated font cache.")
        print(f'{len(fonts)} fonts compiled. {size} bytes written.')