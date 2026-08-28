from celery import shared_task
from django.core.files.base import ContentFile
from django.core.files import File
from PIL import Image
import io
import os

from ad.models import Gallery, Ad


@shared_task(queue='celery:1', autoretry_for=(Exception,), max_retries=3, retry_backoff=True)
def update_ad_thumbnail_async(gallery_id):
    try:
        gallery = Gallery.objects.get(id=gallery_id)
        ad = gallery.ad

        image_file = gallery.image

        # تصویر را با PIL باز کن
        img = Image.open(image_file)

        # تبدیل فرمت رنگی (WebP از شفافیت پشتیبانی می‌کند، اما اگر اصرار به حذف کانال آلفا دارید RGB کنید)
        if img.mode not in ('RGB', 'RGBA'):
            img = img.convert('RGB')

        # ری‌سایز 300x300
        img = img.resize((300, 300), Image.Resampling.LANCZOS)

        # ذخیره داخل buffer به صورت WebP واقعی
        buffer = io.BytesIO()
        # کیفیت ۸۵ برای WebP بسیار عالی و سبک است
        img.save(buffer, format='WEBP', quality=85, method=6)
        buffer.seek(0)

        # استخراج نام فایل بدون پسوند قدیمی و اضافه کردن .webp
        original_filename = os.path.basename(image_file.name)
        name_without_ext, _ = os.path.splitext(original_filename)
        thumbnail_name = f"thumb_{name_without_ext}.webp"

        # ذخیره داخل فیلد thumbnail
        ad.thumbnail.save(thumbnail_name, ContentFile(buffer.read()), save=True)

    except Gallery.DoesNotExist:
        return
