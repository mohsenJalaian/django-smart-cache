# Django Smart Cache

A Django utility for caching successful GET responses with configurable timeouts and optional model-based cache invalidation.

## Features

- Cache successful, non-streaming GET responses.
- Configure the default cache timeout.
- Generate cache keys from request URLs.
- Optionally separate cached responses by user.
- Associate cached responses with Django models for cache invalidation.
- Automatically invalidate registered model cache entries when a model instance is saved or deleted.

## Requirements

- Python 3.10 or later
- Django 4.2 or later

## Installation

Install the package:

```bash
pip install django-smart-cache
```

Add the application configuration to `INSTALLED_APPS` in your Django settings:

```python
INSTALLED_APPS = [
    # Existing applications
    "django_smart_cache.apps.SmartCacheConfig",
]
```

## Configuration

The default cache timeout is 300 seconds.

To change it, add the following setting to your Django project's settings file:

```python
SMART_CACHE_TIMEOUT = 600
```

The value must be a positive integer.

Django Smart Cache uses Django's default cache backend. Configure the `CACHES` setting in your Django project as appropriate for your application.

## Usage

### Basic caching

Import the decorator and apply it to a view:

```python
from django_smart_cache.decorators import smart_cache


@smart_cache(timeout=60)
def article_list(request):
    ...
```

This caches successful, non-streaming HTTP 200 GET responses for 60 seconds.

If `timeout` is omitted, the value of `SMART_CACHE_TIMEOUT` is used.

### Separate cache entries by user

Use `vary_on_user=True` when the response depends on the current user:

```python
@smart_cache(timeout=60, vary_on_user=True)
def my_articles(request):
    ...
```

This includes the user's primary key in the cache key so different users receive separate cache entries.

### Invalidate cache entries when a model changes

Pass a Django model class using the `model` argument:

```python
from .models import Article
from django_smart_cache.decorators import smart_cache


@smart_cache(timeout=60, model=Article)
def article_list(request):
    ...
```

When a response is cached, its cache key is registered for the specified model.

When an instance of that model is saved or deleted, the registered cache entries for that model are invalidated.

## Cache Behavior

- Only HTTP 200 responses are cached.
- Only non-streaming GET responses are stored.
- HEAD requests may reuse an existing cache entry but do not create new entries.
- Requests using other HTTP methods bypass the cache.
- Query strings are included in cache key generation.
- Cache keys can optionally vary by user.
- Model-based invalidation applies to cache entries registered through the `model` argument.

## Security Considerations

Use caution when caching user-specific or sensitive responses.

By default, cache keys do not vary by user. If a view returns different content for different users, use `vary_on_user=True` or an appropriate caching strategy that prevents one user from receiving another user's response.

Review authorization, permissions, and cache invalidation requirements before using this library in production.

## Development

Clone the repository and install the package's build tools:

```bash
python -m pip install setuptools wheel build
```

Run the automated test suite from the project root:

```bash
python -m django test tests --settings=test_settings
```

Build the distribution packages:

```bash
python -m build --no-isolation
```

The generated distribution files are placed in the `dist/` directory.

## Development Status

This project is under active development. The current test suite covers cache key generation, response caching, request handling, and model-based cache invalidation.

Contributions, bug reports, and suggestions are welcome.

## License

MIT
