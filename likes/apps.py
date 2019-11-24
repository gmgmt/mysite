from django.apps import AppConfig


class LikesConfig(AppConfig):
    name = 'likes'

    def ready(self):
        super().ready()
        from . import signals