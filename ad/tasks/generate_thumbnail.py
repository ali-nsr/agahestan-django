from django.core.files.base import ContentFile
from celery import shared_task
from PIL import Image, ImageOps

import io
import logging

logger = logging.getLogger(__name__)

@shared_task(queue='celery:1', autoretry_for=(Exception,), max_retries=3, retry_backoff=True)
def generate_thumbnail(ad, image_field):
    try:
        image_field.open('rb')
        img = Image.open(image_field)
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'RGBA':
                background.paste(img, mask=img.split()[-1])
            else:
                background.paste(img)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        thumb = ImageOps.fit(img, (200, 200), Image.LANCZOS)
        buffer = io.BytesIO()
        thumb.save(buffer, format='JPEG', quality=85, optimize=True)
        buffer.seek(0)

        ad.thumbnail.save(f"thumb_{ad.uuid}.jpg", ContentFile(buffer.read()), save=True)
        buffer.close()
        image_field.close()
    except Exception as e:
        logger.exception(f'Thumbnail failed for {ad.uuid}: {e}')
