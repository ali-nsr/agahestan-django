from django.db.models.signals import post_save
from django.dispatch import receiver
from ad.models import Gallery
from ad.tasks import update_ad_thumbnail_async

@receiver(post_save, sender=Gallery)
def set_main_image_thumbnail(sender, instance, **kwargs):
    if instance.is_main:
        update_ad_thumbnail_async(instance.id)
