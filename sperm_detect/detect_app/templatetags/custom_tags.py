import os
from django import template
from django.utils.text import slugify

register = template.Library()

@register.simple_tag
def update_widget_attrs(field, attrs):
    field.widget.attrs.update(attrs)
    return field
