
from functools import wraps

from django.core.cache import cache

from .cache_key import generate_cache_key
from .cache_registry import register_cache_key
from .conf import get_default_timeout


def smart_cache(timeout=None, model=None, vary_on_user=True):
    if timeout is None:
        timeout = get_default_timeout()

    if not isinstance(timeout, int) or isinstance(timeout, bool):
        raise TypeError("timeout must be an integer.")

    if timeout <= 0:
        raise ValueError("timeout must be greater than zero.")

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Only cache GET and HEAD requests
            if request.method not in ["GET", "HEAD"]:
                return view_func(request, *args, **kwargs)
            if vary_on_user:
                user = getattr(request, "user", None)

                if not getattr(user, "is_authenticated", False):
                    return view_func(request, *args, **kwargs)
            cache_key = generate_cache_key(
                request,
                vary_on_user=vary_on_user,
            )

            cached_response = cache.get(cache_key)

            if cached_response is not None:
                return cached_response

            response = view_func(request, *args, **kwargs)

            # Cache only successful, non-streaming GET responses
            if (
                response.status_code == 200
                and request.method == "GET"
                and not response.streaming
            ):
                cache.set(cache_key, response, timeout)

                if model is not None:
                    model_name = (
                        f"{model._meta.app_label}.{model.__name__}"
                    )
                    register_cache_key(cache_key, model_name)

            return response

        return wrapper

    return decorator
