
from django.test import RequestFactory, SimpleTestCase

from django_smart_cache.cache_key import generate_cache_key


class CacheKeyTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_cache_key_is_generated(self):
        request = self.factory.get("/articles/")

        key = generate_cache_key(request)

        self.assertTrue(key.startswith("smart_cache:"))
        self.assertEqual(len(key), len("smart_cache:") + 64)

    def test_different_query_strings_generate_different_keys(self):
        request1 = self.factory.get("/articles/?page=1")
        request2 = self.factory.get("/articles/?page=2")

        key1 = generate_cache_key(request1)
        key2 = generate_cache_key(request2)

        self.assertNotEqual(key1, key2)

    def test_different_users_generate_different_keys(self):
        request1 = self.factory.get("/profile/")
        request2 = self.factory.get("/profile/")

        request1.user = type("User", (), {"pk": 1})()
        request2.user = type("User", (), {"pk": 2})()

        key1 = generate_cache_key(request1, vary_on_user=True)
        key2 = generate_cache_key(request2, vary_on_user=True)

        self.assertNotEqual(key1, key2)

    def test_same_user_generates_same_key(self):
        request1 = self.factory.get("/profile/")
        request2 = self.factory.get("/profile/")

        request1.user = type("User", (), {"pk": 1})()
        request2.user = type("User", (), {"pk": 1})()

        key1 = generate_cache_key(request1, vary_on_user=True)
        key2 = generate_cache_key(request2, vary_on_user=True)

        self.assertEqual(key1, key2)

    def test_anonymous_request_generates_stable_user_specific_key(self):
        request1 = self.factory.get("/profile/")
        request2 = self.factory.get("/profile/")

        key1 = generate_cache_key(request1, vary_on_user=True)
        key2 = generate_cache_key(request2, vary_on_user=True)

        self.assertEqual(key1, key2)