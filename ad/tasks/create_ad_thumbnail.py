from celery import shared_task
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys
import os
from ad.models import Ad


@shared_task(queue='celery:1', autoretry_for=(Exception,), max_retries=3, retry_backoff=True)
def create_ad_thumbnail_async(image_from_gallery, ad_id):
    # ad = Ad.objects.get(id=ad_id)
    #
    # output_size = (300, 169)
    # output_thumb = BytesIO()
    #
    # img = Image.open(image_from_gallery)
    # img_name = image_from_gallery.photo.name.split('.')[0]
    #
    # if img.height > 300 or img.width > 300:
    #     img.thumbnail(output_size)
    #     img.save(output_thumb, format='JPEG', quality=90)
    #
    # ad.thumbnail = InMemoryUploadedFile(output_thumb, 'ImageField', f"{img_name}_thumb.jpg", 'image/jpeg',
    #                                        sys.getsizeof(output_thumb), None)
    ad = Ad.objects.get(id=ad_id)

    output_size = (300, 169)
    output_thumb = BytesIO()

    img = Image.open(image_from_gallery)
    img_name = os.path.splitext(image_from_gallery.photo.name)[0]

    if img.height > 300 or img.width > 300:
        img.thumbnail(output_size)

    # تبدیل واقعی به webp
    img.save(output_thumb, format='WEBP', quality=90, method=6)
    output_thumb.seek(0)

    ad.thumbnail = InMemoryUploadedFile(
        output_thumb,
        field_name='ImageField',
        name=f"{img_name}_thumb.webp",
        content_type='image/webp',
        size=output_thumb.getbuffer().nbytes,
        charset=None
    )
    ad.save()