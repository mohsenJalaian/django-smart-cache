
SECRET_KEY = "test-secret-key"

DEBUG = True

INSTALLED_APPS = [
    "django_smart_cache.apps.SmartCacheConfig",
    "testapp",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}
MIGRATION_MODULES = {
    "testapp": None,
}