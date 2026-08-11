from django.apps import AppConfig


class MapapiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Mapapi'

    def ready(self):
        from . import signals
        from .firebase_app import init_firebase
        init_firebase()
