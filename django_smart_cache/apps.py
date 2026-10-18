
from django.apps import AppConfig


class SmartCacheConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_smart_cache"

    def ready(self):
        from . import signals  # noqa: F401
