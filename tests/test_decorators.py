
from unittest.mock import Mock, patch

from django.core.cache import cache
from django.http import HttpResponse, StreamingHttpResponse
from django.test import (
    RequestFactory,
    SimpleTestCase,
    override_settings,
)

from django_smart_cache.cache_key import generate_cache_key
from django_smart_cache.cache_registry import REGISTRY_KEY
from django_smart_cache.decorators import smart_cache
from testapp.models import TestArticle


class SmartCacheTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        cache.clear()

    def authenticated_request(self, path):
        request = self.factory.get(path)
        request.user = type(
            "User",
            (),
            {"pk": 1, "is_authenticated": True},
        )()
        return request

    @patch("django_smart_cache.decorators.cache")
    def test_get_response_is_cached(self, mock_cache):
        mock_cache.get.return_value = None

        @smart_cache(timeout=60)
        def my_view(request):
            return HttpResponse("Hello")

        request = self.authenticated_request("/test/")
        response = my_view(request)

        self.assertEqual(response.status_code, 200)
        mock_cache.set.assert_called_once()

    @patch("django_smart_cache.decorators.cache")
    def test_post_response_is_not_cached(self, mock_cache):
        @smart_cache(timeout=60)
        def my_view(request):
            return HttpResponse("Created")

        request = self.factory.post("/test/")
        response = my_view(request)

        self.assertEqual(response.status_code, 200)
        mock_cache.get.assert_not_called()
        mock_cache.set.assert_not_called()

    @patch("django_smart_cache.decorators.cache")
    def test_error_response_is_not_cached(self, mock_cache):
        mock_cache.get.return_value = None

        @smart_cache(timeout=60)
        def my_view(request):
            return HttpResponse("Not found", status=404)

        request = self.factory.get("/missing/")
        response = my_view(request)

        self.assertEqual(response.status_code, 404)
        mock_cache.set.assert_not_called()

    @patch("django_smart_cache.decorators.cache")
    def test_cached_response_is_reused(self, mock_cache):
        cached_response = HttpResponse("Cached Hello")
        mock_cache.get.return_value = cached_response

        @smart_cache(timeout=60)
        def my_view(request):
            return HttpResponse("Fresh Hello")

        request = self.authenticated_request("/test/")
        response = my_view(request)

        self.assertEqual(response.content, b"Cached Hello")
        mock_cache.set.assert_not_called()

    @patch("django_smart_cache.decorators.cache")
    def test_streaming_response_is_not_cached(self, mock_cache):
        mock_cache.get.return_value = None

        @smart_cache(timeout=60)
        def my_view(request):
            return StreamingHttpResponse(iter([b"Hello"]))

        request = self.factory.get("/stream/")
        response = my_view(request)

        self.assertTrue(response.streaming)
        mock_cache.set.assert_not_called()

    def test_zero_timeout_is_rejected(self):
        with self.assertRaises(ValueError):
            smart_cache(timeout=0)

    def test_negative_timeout_is_rejected(self):
        with self.assertRaises(ValueError):
            smart_cache(timeout=-10)

    def test_string_timeout_is_rejected(self):
        with self.assertRaises(TypeError):
            smart_cache(timeout="60")

    def test_float_timeout_is_rejected(self):
        with self.assertRaises(TypeError):
            smart_cache(timeout=60.5)

    def test_boolean_timeout_is_rejected(self):
        with self.assertRaises(TypeError):
            smart_cache(timeout=True)

    @patch("django_smart_cache.decorators.cache")
    def test_default_timeout_is_used(self, mock_cache):
        mock_cache.get.return_value = None

        @smart_cache()
        def my_view(request):
            return HttpResponse("Hello")

        request = self.authenticated_request("/test/")
        my_view(request)

        mock_cache.set.assert_called_once()
        self.assertEqual(mock_cache.set.call_args.args[2], 300)

    @override_settings(SMART_CACHE_TIMEOUT=120)
    @patch("django_smart_cache.decorators.cache")
    def test_custom_default_timeout_is_used(self, mock_cache):
        mock_cache.get.return_value = None

        @smart_cache()
        def my_view(request):
            return HttpResponse("Hello")

        request =self.authenticated_request("/test/")
        my_view(request)

        mock_cache.set.assert_called_once()
        self.assertEqual(mock_cache.set.call_args.args[2], 120)

    @patch("django_smart_cache.decorators.cache")
    def test_vary_on_user_uses_user_specific_cache_key(self, mock_cache):
        mock_cache.get.return_value = None

        @smart_cache(timeout=60, vary_on_user=True)
        def my_view(request):
            return HttpResponse("Hello")

        request1 = self.factory.get("/profile/")
        request1.user = type(
             "User",
              (),
              {"pk": 1, "is_authenticated": True},
        )()


        request2 = self.factory.get("/profile/")
        request2.user = type(
            "User",
            (),
            {"pk": 2, "is_authenticated": True},
        )()

        my_view(request1)
        my_view(request2)

        self.assertEqual(mock_cache.get.call_count, 2)

        first_key = mock_cache.get.call_args_list[0].args[0]
        second_key = mock_cache.get.call_args_list[1].args[0]

        self.assertNotEqual(first_key, second_key)

    def test_head_response_is_not_cached(self):
        request = self.factory.head("/articles/")

        view = Mock(return_value=HttpResponse("Article list"))
        decorated_view = smart_cache()(view)

        decorated_view(request)

        view.assert_called_once_with(request)

    def test_model_cache_key_is_registered(self):
        request =  self.authenticated_request("/articles/")

        view = Mock(return_value=HttpResponse("Article list"))
        decorated_view = smart_cache(model=TestArticle)(view)

        decorated_view(request)

        cache_key = generate_cache_key(request, vary_on_user=True)
        registry = cache.get(REGISTRY_KEY, {})

        self.assertIn(
            cache_key,
            registry.get("testapp.TestArticle", []),
        )

    def test_error_response_does_not_register_model_cache_key(self):
        request = self.factory.get("/articles/")

        view = Mock(
            return_value=HttpResponse("Not found", status=404)
        )
        decorated_view = smart_cache(model=TestArticle)(view)

        decorated_view(request)

        cache_key = generate_cache_key(request)
        registry = cache.get(REGISTRY_KEY, {})

        self.assertNotIn(
            cache_key,
            registry.get("testapp.TestArticle", []),
        )

    def test_different_users_receive_separate_cached_responses(self):
        request1 = self.factory.get("/profile/")
        request1.user = type(
            "User",
            (),
            {"pk": 1, "is_authenticated": True},
        )()

        request2 = self.factory.get("/profile/")
        request2.user = type(
            "User",
            (),
            {"pk": 2, "is_authenticated": True},
        )()

        view = Mock(
            side_effect=[
                HttpResponse("User 1"),
                HttpResponse("User 2"),
            ]
        )
        decorated_view = smart_cache(vary_on_user=True)(view)

        response1 = decorated_view(request1)
        response2 = decorated_view(request2)

        self.assertEqual(response1.content, b"User 1")
        self.assertEqual(response2.content, b"User 2")
        self.assertEqual(view.call_count, 2)

    def test_cached_response_does_not_call_view_again(self):
        request = self.authenticated_request("/articles/")

        view = Mock(return_value=HttpResponse("Article list"))
        decorated_view = smart_cache(model=TestArticle)(view)

        first_response = decorated_view(request)
        second_response = decorated_view(request)

        self.assertEqual(first_response.content, second_response.content)
        view.assert_called_once_with(request)


    def test_default_cache_key_is_user_specific(self):
        request1 = self.factory.get("/profile/")
        request1.user = type("User", (), {"pk": 1})()

        request2 = self.factory.get("/profile/")
        request2.user = type("User", (), {"pk": 2})()

        key1 = generate_cache_key(request1)
        key2 = generate_cache_key(request2)

        self.assertNotEqual(key1, key2)

    @patch("django_smart_cache.decorators.cache")
    def test_anonymous_user_bypasses_cache_by_default(self, mock_cache):
            request = self.factory.get("/profile/")
            request.user = type(
                "AnonymousUser",
                (),
                {"is_authenticated": False},
            )()

            view = Mock(return_value=HttpResponse("Anonymous response"))
            decorated_view = smart_cache()(view)

            response = decorated_view(request)

            self.assertEqual(response.content, b"Anonymous response")
            mock_cache.get.assert_not_called()
            mock_cache.set.assert_not_called()
            view.assert_called_once_with(request)