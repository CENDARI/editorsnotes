from django import template

register = template.Library()

@register.filter(name='notzero')
def notzero(value):
    if value==0:
        return ''
    return '(%d)'%value
