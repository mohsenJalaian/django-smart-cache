
from django.conf import settings


DEFAULT_TIMEOUT = 300


def get_default_timeout():
    return getattr(
        settings,
        "SMART_CACHE_TIMEOUT",
        DEFAULT_TIMEOUT,
    )
