from django.apps import AppConfig


class CommentConfig(AppConfig):
    name = 'comment'

    def ready(self):
        super().ready()
        from . import signals