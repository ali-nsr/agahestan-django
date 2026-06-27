from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.cache import cache

from ..models import Ad

from ..tasks import gallery_image_resize_async


@receiver(post_save, sender=Ad)
def set_ad_list_cache(sender, instance, created, **kwargs):
    qs = Ad.objects.select_related('category', 'province', 'city', 'neighborhood')
    cache.set(
        f'ad:ads',
        qs,
        timeout=60,
    )
