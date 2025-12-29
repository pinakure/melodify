from django.core.management.base import BaseCommand
from main.models import Scheme
from .scan import saferead
import stable_whisper
import os 

class Command(BaseCommand):
    help = "Generates lyrics for requested song"

    def add_arguments(self, parser):
        parser.add_argument("filename"  , nargs="+", type=str)
        parser.add_argument("--language", '-l', default=['es']    ,nargs="*", type=str)
        parser.add_argument("--model"   , '-m', default=['small'] ,nargs="*", type=str)

    def handle(self, *args, **options):
        filename = options['filename'][0]
        language = options['language'][0]
        __model  = options['model'][0]
        srtfile  = filename.split('.mp3')[0]+'.srt'
        print(f'Initializing Stable Whisper ({__model}) model...') 
        # 'small' es rápido; 'medium' es mejor para música si tienes buena RAM/GPU
        model = stable_whisper.load_model(__model)

        # 'mel_filters' mejorados ayudan a ignorar un poco el ruido musical
        print(f'Analyzing ({language}) {filename}...') 
        result = model.transcribe(filename, language=language, fp16=False) 

        print(f"Generating { srtfile }...")
        result.to_srt_vtt( srtfile, word_level=False ) #segment_level=False # Esto mantiene la sincronización por palabra pero limpia el formato
