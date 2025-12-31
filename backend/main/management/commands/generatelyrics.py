from django.core.management.base import BaseCommand
from main.models import Scheme
from main.utils import saferead
import os 

class Command(BaseCommand):
    help = "Generates lyrics for requested song"

    def add_arguments(self, parser):
        parser.add_argument("filename"  , nargs="+", type=str)
        parser.add_argument("--language", '-l', default=['es']    ,nargs="*", type=str)
        parser.add_argument("--model"   , '-m', default=['small'] ,nargs="*", type=str)

    def initialize(self, model):
        import stable_whisper
        print(f'Initializing Stable Whisper ({model}) model...') 
        # 'small' es rápido; 'medium' es mejor para música si tienes buena RAM/GPU
        self.model = stable_whisper.load_model(model)

    def work(self, filename, language):
        # 'mel_filters' mejorados ayudan a ignorar un poco el ruido musical
        print(f'Analyzing ({language}) {filename}...') 
        result = self.model.transcribe(filename, language=language, fp16=False) 

        srtfile  = filename.rstrip('.mp3')+'.srt'
        karfile  = filename.rstrip('.mp3')+'.kar'
        print(f"Generating { srtfile }...")
        result.to_srt_vtt( karfile, word_level=True  ) #segment_level=False # Esto mantiene la sincronización por palabra pero limpia el formato
        result.to_srt_vtt( srtfile, word_level=False ) #segment_level=False # Esto mantiene la sincronización por palabra pero limpia el formato

    def handle(self, *args, **options):
        filename = options['filename'][0]
        language = options['language'][0]
        model    = options['model'   ][0]
        self.initialize(model)
        self.work(filename, language)