from django.core.cache import cache
from django.test import SimpleTestCase

from django_smart_cache.cache_registry import (
    REGISTRY_KEY,
    register_cache_key,
    clear_model_cache,
)


class CacheRegistryTests(SimpleTestCase):
    def setUp(self):
        cache.clear()

    def test_cache_key_is_registered(self):
        register_cache_key("cache:key:1", "blog.Post")

        registry = cache.get(REGISTRY_KEY)

        self.assertIn("blog.Post", registry)
        self.assertIn("cache:key:1", registry["blog.Post"])

    def test_model_cache_is_cleared(self):
        cache.set("cache:key:1", "cached response")

        register_cache_key("cache:key:1", "blog.Post")
        clear_model_cache("blog.Post")

        self.assertIsNone(cache.get("cache:key:1"))

    def test_clearing_one_model_preserves_other_model(self):
        cache.set("cache:key:1", "post response")
        cache.set("cache:key:2", "product response")

        register_cache_key("cache:key:1", "blog.Post")
        register_cache_key("cache:key:2", "shop.Product")

        clear_model_cache("blog.Post")

        self.assertIsNone(cache.get("cache:key:1"))
        self.assertEqual(cache.get("cache:key:2"), "product response")