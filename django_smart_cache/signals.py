
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .cache_registry import clear_model_cache


@receiver(post_save)
def model_saved(sender, instance, **kwargs):
    if not hasattr(sender, "_meta"):
        return

    model_name = f"{sender._meta.app_label}.{sender.__name__}"
    clear_model_cache(model_name)


@receiver(post_delete)
def model_deleted(sender, instance, **kwargs):
    if not hasattr(sender, "_meta"):
        return

    model_name = f"{sender._meta.app_label}.{sender.__name__}"
    clear_model_cache(model_name)
