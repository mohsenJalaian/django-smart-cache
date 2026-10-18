from django.core.cache import cache
from django.test import TestCase

from django_smart_cache.cache_registry import register_cache_key
from testapp.models import TestArticle


class CacheSignalTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_saving_model_clears_its_cache(self):
        cache_key = "smart_cache:test_article"
        cache.set(cache_key, "cached response")

        register_cache_key(
            cache_key,
            "testapp.TestArticle",
        )

        TestArticle.objects.create(title="First article")

        self.assertIsNone(cache.get(cache_key))

    def test_deleting_model_clears_its_cache(self):
        article = TestArticle.objects.create(title="Article to delete")

        cache_key = "smart_cache:test_article"
        cache.set(cache_key, "cached response")

        register_cache_key(
            cache_key,
            "testapp.TestArticle",
        )

        article.delete()

        self.assertIsNone(cache.get(cache_key))

    def test_saving_model_preserves_other_model_cache(self):
        cache_key = "smart_cache:other_model"
        cache.set(cache_key, "other model response")

        register_cache_key(
            cache_key,
            "shop.Product",
        )

        TestArticle.objects.create(title="New article")

        self.assertEqual(
            cache.get(cache_key),
            "other model response",
        )