from django.conf import settings
from pathlib import Path
import os

def debug(text):
    #return
    with open(settings.LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(text+'\n')

def saferead(filename, read_mode='r'):
    if settings.ANDROID:
        BASE_DIR = Path(__file__).resolve().parent
        filename = BASE_DIR / filename
    debug(f"SAFEREAD :: Trying to open '{filename}'")
    with open(filename, read_mode) as f:
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
    
    payload = saferead(file)
    return payload.split('\n')

def load_dict(file):
    if os.path.splitext(os.path.basename(__file__))[0] == 'main':
        file = os.path.join(os.path.dirname(__file__), 'config', file)
    else:
        file = os.path.join('config', file)
        
    payload = {}
    
    elements = saferead(file).split('\n')
    for element in elements:
        if len(element)==0:continue
        items = element.split('=')
        key = items[0]
        value = items[1].split(',')
        payload[key] = [ x.strip() for x in value ]
    return payload

def dump_picture(filename, data):
    # Guarda los datos binarios de la imagen en un archivo
    with open(filename, 'wb') as img_file:
        img_file.write(data)