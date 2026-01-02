from django import template

register = template.Library()

@register.filter(name="strftime")
def strftime(value, arg):
    timestamp = str(value).split('.')[0].lstrip('0') #discard miliseconds and strip hour heading zeros
    if timestamp[0] == ':':
        timestamp = timestamp.lstrip(':') # remove : if no hours present
    timestamp = timestamp.lstrip('0') #remove heading minute zeros, if any
    return timestamp

@register.filter(name="get_next_song_id")
def get_next_song_id(songs, position):
    return songs[position+1].id

@register.filter(name="replace")
def replace(value, arg):
    """Uso: {{ texto|replace:"_, " }} reemplaza guiones por espacios"""
    original, reemplazo = arg.split(',')
    return str(value).replace(original, reemplazo)