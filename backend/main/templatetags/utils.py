from django import template

register = template.Library()

@register.filter(name="strftime")
def strftime(value, arg):
    timestamp = str(value).split('.')[0].lstrip('0') #discard miliseconds and strip hour heading zeros
    if timestamp[0] == ':':
        timestamp = timestamp.lstrip(':') # remove : if no hours present
    timestamp = timestamp.lstrip('0') #remove heading minute zeros, if any
    return timestamp