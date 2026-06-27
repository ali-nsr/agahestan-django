from celery import shared_task
from django.core.files.base import ContentFile
from django.core.files import File
from PIL import Image
import io

from ad.models import Gallery, Ad


@shared_task(queue='celery:1', autoretry_for=(Exception,), max_retries=3, retry_backoff=True)
def update_ad_thumbnail_async(gallery_id):
    try:
        gallery = Gallery.objects.get(id=gallery_id)
        ad = gallery.ad

        image_file = gallery.image

        # تصویر را با PIL باز کن
        img = Image.open(image_file)

        # تبدیل به RGB برای جلوگیری از خطا روی PNG با آلفا
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # ری‌سایز 300x300
        img = img.resize((300, 300), Image.Resampling.LANCZOS)

        # ذخیره داخل buffer
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=85)
        buffer.seek(0)

        # ساخت نام جدید
        thumbnail_name = f"thumb_{image_file.name.split('/')[-1]}"

        # ذخیره داخل فیلد thumbnail
        ad.thumbnail.save(thumbnail_name, ContentFile(buffer.read()), save=True)

    except Gallery.DoesNotExist:
        return
