from django import template
import time

register = template.Library()

@register.filter(name='todate')
def todate(value):
    if value is None:
        return ''
    t = time.localtime(value/1000.0)
    return '%04d-%02d-%02d' % (t.tm_year, t.tm_mon, t.tm_mday)
