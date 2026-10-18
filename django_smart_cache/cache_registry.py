
from django.core.cache import cache

REGISTRY_KEY = "smart_cache:registry"


def register_cache_key(cache_key, model_name):
    registry = cache.get(REGISTRY_KEY, {})

    model_keys = set(registry.get(model_name, []))
    model_keys.add(cache_key)

    registry[model_name] = list(model_keys)

    cache.set(REGISTRY_KEY, registry, timeout=None)


def clear_model_cache(model_name):
    registry = cache.get(REGISTRY_KEY, {})

    keys = registry.pop(model_name, [])

    if keys:
        cache.delete_many(keys)

    cache.set(REGISTRY_KEY, registry, timeout=None)
