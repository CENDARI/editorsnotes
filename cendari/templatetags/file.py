from django import template
import os.path

register = template.Library()

@register.filter(name='basename')
def filename(path):
    if path=='':
        return ''
    return os.path.basename(path)
