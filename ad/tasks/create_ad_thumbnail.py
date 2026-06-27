from celery import shared_task
from PIL import Image
from django.core.files.storage import default_storage
import sys
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile


from ad.models import Ad

@shared_task(queue='celery:1', autoretry_for=(Exception,), max_retries=3, retry_backoff=True)
def create_ad_thumbnail_async(image_from_gallery, ad_id):
    ad = Ad.objects.get(id=ad_id)

    output_size = (300, 169)
    output_thumb = BytesIO()

    img = Image.open(image_from_gallery)
    img_name = image_from_gallery.photo.name.split('.')[0]

    if img.height > 300 or img.width > 300:
        img.thumbnail(output_size)
        img.save(output_thumb, format='JPEG', quality=90)

    ad.thumbnail = InMemoryUploadedFile(output_thumb, 'ImageField', f"{img_name}_thumb.jpg", 'image/jpeg',
                                           sys.getsizeof(output_thumb), None)
