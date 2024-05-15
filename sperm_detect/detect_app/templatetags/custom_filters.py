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


@register.filter
def calc_x(value, arg_w):
    return (value-arg_w/2) * 1920

@register.filter
def calc_y(value, arg_h):
    return (value-arg_h/2) * 1080

@register.filter
def calc_w(value):
    return value * 1920

@register.filter
def calc_h(value):
    return value * 1080