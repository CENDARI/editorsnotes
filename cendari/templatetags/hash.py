from django import template

register = template.Library()

@register.filter(name='hash')
def hash(h, key):
    return h[key]

@register.filter(name='has_key')
def has_key(h, key):
    return key in h
