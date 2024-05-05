from django.apps import AppConfig
from django import template
from .templatetags import custom_filters  # Import your custom filters


class DetectAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'detect_app'
    def ready(self):
            import detect_app.signals 
            register = template.Library()
            register.filter('basename', custom_filters.basename)  # Example filter 