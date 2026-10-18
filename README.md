
# Django Smart Cache

A Django utility for caching successful GET responses with configurable
timeouts and optional model-based cache invalidation.

## Features

- Cache successful, non-streaming GET responses.
- Configure the default cache timeout.
- Generate cache keys from request URLs.
- Optionally vary cache keys by user.
- Associate cached responses with Django models for invalidation.

## Installation

Install the package:

```bash
pip install django-smart-cache
```

Add the application to `INSTALLED_APPS` in your Django settings:

```python
INSTALLED_APPS = [
    # Existing applications
    "django_smart_cache.apps.SmartCacheConfig",
]
```

## Configuration

The default cache timeout is 300 seconds. You can change it in
your Django settings:

```python
SMART_CACHE_TIMEOUT = 600
```

## Usage

Import the decorator:

```python
from django_smart_cache.decorators import smart_cache
```

Cache a view for 60 seconds:

```python
@smart_cache(timeout=60)
def article_list(request):
    ...
```

Vary the cache by user:

```python
@smart_cache(timeout=60, vary_on_user=True)
def my_articles(request):
    ...
```

Associate cached responses with a model:

```python
from .models import Article

@smart_cache(timeout=60, model=Article)
def article_list(request):
    ...
```

## Django Cache Backend

Configure a Django cache backend in your project settings.
The library uses Django's default cache backend.

## Development Status

This project is under development. Automated tests and compatibility
checks are required before production use.

## License

MIT
