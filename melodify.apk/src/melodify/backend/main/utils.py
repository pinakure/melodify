from config.forbidden   import FORBIDDEN_CHARACTERS, EMOJI_REPLACEMENT, CODENAME_PREFIXES, FORBIDDEN_FOLDERS, FORBIDDEN_PREFIXES, FORBIDDEN_SUFFIXES, FORBIDDEN_TAGS
from django.utils       import timezone
from django.conf        import settings
from datetime           import datetime
from pathlib            import Path
import hashlib
import os

def debug(text, **kwargs):
    return Utils.debug(text, **kwargs)

class Utils:    

    LIBRARY_ROOT = None

    def library_path(folder=''):
        if Utils.LIBRARY_ROOT: return os.path.join( Utils.LIBRARY_ROOT, folder )
        Utils.LIBRARY_ROOT = Path(Utils.saferead('config/library-root.cfg').strip('\n')).resolve() 
        return os.path.join( Utils.LIBRARY_ROOT, folder )
    
    def debug(text, **kwargs):
        #return
        with open(settings.LOG_FILE, 'a', encoding='utf-8', **kwargs) as f:
            f.write(text+'\n')

    def saferead(filename, read_mode='r', **args):
        if settings.ANDROID:
            BASE_DIR = Path(__file__).resolve().parent
            filename = BASE_DIR / filename
        debug(f"SAFEREAD :: Trying to open '{filename}'")
        with open(filename, read_mode, **args) as f:
            return f.read()
            
    def safewrite(filename, contents, binary=False):
        if settings.ANDROID:
            BASE_DIR = Path(__file__).resolve().parent
            filename = BASE_DIR / filename
        debug(f"SAFEWRITE :: Trying to open '{filename}'")
        with open(filename, 'w' if not binary else 'wb') as f:
            return f.write(contents)
        
    def load_array(file):
        if os.path.splitext(os.path.basename(__file__))[0] == 'main':
            file = os.path.join(os.path.dirname(__file__), 'config', file)
        else:
            file = os.path.join('config', file)
        
        payload = []
        
        payload = Utils.saferead(file)
        return payload.split('\n')

    def load_dict(file):
        if os.path.splitext(os.path.basename(__file__))[0] == 'main':
            file = os.path.join(os.path.dirname(__file__), 'config', file)
        else:
            file = os.path.join('config', file)
            
        payload = {}
        
        elements = Utils.saferead(file).split('\n')
        for element in elements:
            if len(element)==0:continue
            items = element.split('=')
            key = items[0]
            value = items[1].split(',')
            payload[key] = [ x.strip() for x in value ]
        return payload
        
    def dump_picture(filename, data):
        """Guarda los datos binarios de la imagen en un archivo."""
        with open(filename, 'wb') as img_file:
            img_file.write(data)

    def get_hash(path : str):
        """Devuelve un hash de 128 caracteres ASCII (SHA-512 en hex) para un fichero MP3."""
        sha = hashlib.sha512()
        with open(path, "rb") as f:
            # Leer en bloques para archivos grandes
            for chunk in iter(lambda: f.read(8192), b""):
                sha.update(chunk)
        return sha.hexdigest()  # 128 caracteres ASCII

    def is_number(var):
        try:
            return isinstance(int(var), int)
        except:
            return False
    
    def is_timestamp(tag):
        if '/' in tag or '\\' in tag:
            return ''
        if len(tag) == 4:
            # YYYY
            if Utils.is_number(tag):
                return f'{tag}0101'
        if len(tag) == 7:
            # YYYY-MM
            if Utils.is_number(tag[0:4]):
                if Utils.is_number(tag[5:7]):
                    return f'{tag[0:4]}{tag[5:7]}01'
            # MM-YYYY
            else:
                if Utils.is_number(tag[0:2]):
                    if Utils.is_number(tag[3:7]):
                        return f'{tag[3:7]}{tag[0:2]}01'
            return ''
        if len(tag) == 8:
            if Utils.is_number(tag[0:4]):
                if int(tag[0:4]) < 2500:
                    if not Utils.is_number(tag[6:8]):
                        # YYYYMMXX
                        return f'{tag[0:4]}{tag[4:6]}01'
                    elif not Utils.is_number(tag[4:6]):
                        # YYYYXXXX
                        if Utils.is_number(tag[0:4]):
                            return f'{tag[0:4]}0101'
                    else:
                        # YYYYMMDD
                        return f'{tag[0:4]}{tag[4:6]}{tag[6:8]}'
            elif Utils.is_number(tag[0:2]):
                # DD-MM-YY
                if not Utils.is_number(tag[2]):
                    if Utils.is_number(tag[3:5]):
                        if not Utils.is_number(tag[5]):
                            if Utils.is_number(tag[6:8]):
                                return f'20{tag[0:2]}{tag[3:5]}{tag[6:8]}'
            return ''
        if len(tag) == 10:
            # 0000-00-00
            if Utils.is_number(tag[0:4]):
                if Utils.is_number(tag[5:7]):
                    if Utils.is_number(tag[8:10]):
                        return f'{tag[0:4]}{tag[5:7]}{tag[8:10]}'
            # 00-00-0000
            if Utils.is_number(tag[0:2]):
                if Utils.is_number(tag[3:5]):
                    if Utils.is_number(tag[6:10]):
                        return f'{tag[6:10]}{tag[3:5]}{tag[0:2]}'
            return ''
        return ''

    def is_codename(tag: str) -> bool:
        """Devuelve True si la tag es un codename."""
        for prefix in CODENAME_PREFIXES:
            if tag.startswith(prefix) : return True
        return False
    
    def is_empty(text):
        return len(text.strip(' ').strip('\n').strip('\t')) == 0

    def is_ignored_path(path: str) -> bool:
        """Devuelve True si la ruta está dentro de alguna carpeta ignorada."""
        p = Path(path).resolve()

        # Comprobamos cada parte del path
        for part in p.parts:
            for folder in FORBIDDEN_FOLDERS:
                if part.startswith(folder):return True

        return False

    def is_comment_tag(tag: str) -> bool:
        """Devuelve True si la tag tiene espacios"""
        return " " in tag

    def is_forbidden_tag(tag: str) -> bool:
        """Devuelve True si la tag está prohibida."""
        for fb in FORBIDDEN_TAGS: 
            if fb == tag.lower(): return True
        for fb in FORBIDDEN_PREFIXES:
            if tag.lower().startswith(fb): return True
        for fb in FORBIDDEN_SUFFIXES:
            if tag.lower().endswith(fb): return True
        return False

class Sanitizer:
    def clean(text):
        text = text.replace('/','')
        text = text.replace('&','and')
        text = text.replace('"','')
        return text

    def filename(text):
        for target in FORBIDDEN_CHARACTERS:
            text = text.replace(target, '')
        return text    

    def year(year : str):
        year = year.split('-')[0]
        if int(year)<1000: return "1000"
        return year

    def name(name):
        return name.strip().lower().title()

    def tag(tag, song):
        if Utils.is_empty(tag) or Utils.is_forbidden_tag(tag):
            return ""
        if Utils.is_codename(tag):
            song.codename = tag
            return ""
        if Utils.is_comment_tag(tag):
            song.comment += tag
            return ""

        timestamp = Utils.is_timestamp(tag)
        if len(timestamp) > 0:
            song.timestamp = timezone.make_aware(datetime(int(timestamp[0:4]),int(timestamp[4:6]),int(timestamp[6:8])))
            return ""
        if Utils.is_number(tag):
            return ""
        tag = tag.replace(' - ', ', ')
        for emoji,key in EMOJI_REPLACEMENT.items():
            tag = tag.replace(key, emoji)

        tag = tag.rstrip()
        tag = tag.rstrip('.')
        return tag
    
    def artists( artist_name ):
        FEAT_TAGS = [
            ' ft.'      ,
            ' ft '      ,
            ' feat.'    ,
            ' feat '    ,
            ' prod.'    ,
            ' prod '    ,
            '/'         ,
            '\\'        ,
            ','         ,
            ' vs.'      ,
            ' vs '      ,
            ' versus '  ,
            ' versus.'  ,
        ]
        artist  = artist_name.lower()
        for tag in FEAT_TAGS:
            artist=artist.replace(tag, '|')
        return [ q.lstrip().rstrip().title() for q in artist.split('|')]
