from django.apps import AppConfig


class DetectAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'detect_app'
    def ready(self):
            import detect_app.signals 