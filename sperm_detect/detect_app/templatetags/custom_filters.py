import os
from django import template
from django.utils.text import slugify

register = template.Library()

@register.filter(name='basename')
def basename(value):
    return os.path.basename(value)

@register.filter(name='remove_extension')
def remove_extension(value):
    base_name = os.path.basename(value)
    name_only, _ = os.path.splitext(base_name)
    return name_only