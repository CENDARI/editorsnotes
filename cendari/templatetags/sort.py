from django import template
from django.utils.datastructures import SortedDict

register = template.Library()

@register.filter(name='sortiter')
def listsort(value):
    if isinstance(value, dict):
        new_dict = SortedDict()
        key_list = value.keys()
        key_list.sort()
        for key in key_list:
            new_dict[key] = value[key]
        return new_dict.items()
    elif isinstance(value, list):
        new_list = list(value)
        new_list.sort()
        return new_list.iter()
    else:
        return value
    listsort.is_safe = True
