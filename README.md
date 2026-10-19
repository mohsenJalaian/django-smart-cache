# Django Smart Cache

A Django utility for caching successful GET responses with configurable timeouts and optional model-based cache invalidation.

## Features

- Cache successful, non-streaming GET responses.
- Configure the default cache timeout.
- Generate cache keys from request URLs.
- Separate cached responses by authenticated user by default.
- Bypass caching for anonymous users by default, with an option for shared public caching.
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

By default, `vary_on_user=True`. Authenticated users receive separate cache entries based on their user ID, while anonymous requests bypass the cache.

```python
@smart_cache(timeout=60)
def my_articles(request):
    ...
```

For public views that return identical content to all users, set `vary_on_user=False` to enable shared caching, including for anonymous users:

```python
@smart_cache(timeout=60, vary_on_user=False)
def public_articles(request):
    ...
```

Only use shared caching when the response does not contain user-specific or sensitive content.

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
- HEAD requests bypass