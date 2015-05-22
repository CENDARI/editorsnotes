from django import template
from django.utils.datastructures import SortedDict

register = template.Library()

@register.filter(name='notzero')
def notzero(value):
    if value==0:
        return ''
    return '(%d)'%value
