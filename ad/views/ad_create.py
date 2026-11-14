from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import transaction

from PIL import Image, ImageOps

import io
import logging

from ad.models import Category, Gallery
from ad.forms import (
    AdForm, build_category_form, save_category_attributes,
    validate_image, MAX_IMAGES,
)

logger = logging.getLogger(__name__)


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


@login_required
def ad_create(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug, children__isnull=True)

    if not category.get_category_fields().exists():
        messages.error(request, 'این دسته‌بندی امکان ثبت آگهی ندارد.')
        return redirect('ad:choose-category')

    if request.method == 'POST':
        form = AdForm(request.POST, request.FILES, user=request.user, fixed_category=category)
        cat_form = build_category_form(category, data=request.POST)

        images = request.FILES.getlist('images')
        image_errors = []

        if not images:
            image_errors.append('حداقل یک تصویر آپلود کنید.')
        if len(images) > MAX_IMAGES:
            image_errors.append(f'حداکثر {MAX_IMAGES} تصویر مجاز است.')
        for img in images:
            try:
                validate_image(img)
            except ValidationError as e:
                image_errors.extend(e.messages)

        try:
            main_index = int(request.POST.get('main_image_index', 0))
            if not (0 <= main_index < max(len(images), 1)):
                main_index = 0
        except (ValueError, TypeError):
            main_index = 0

        if form.is_valid() and cat_form.is_valid() and not image_errors:
            try:
                with transaction.atomic():
                    ad = form.save()
                    save_category_attributes(ad, cat_form.cleaned_data, category)

                    gallery_items = []
                    for i, img in enumerate(images):
                        gallery_items.append(
                            Gallery.objects.create(
                                ad=ad, image=img,
                                is_main=(i == main_index),
                            )
                        )

                    if gallery_items:
                        generate_thumbnail(ad, gallery_items[main_index].image)

                messages.success(request, 'آگهی شما ثبت شد و در انتظار تأیید است.')
                return redirect('accounts:dashboard')
            except Exception as e:
                logger.exception(f'Ad create failed: {e}')
                messages.error(request, f'خطا در ثبت آگهی: {e}')
        else:
            # نمایش خطاها برای دیباگ
            if not form.is_valid():
                logger.warning(f'AdForm errors: {form.errors}')
            if not cat_form.is_valid():
                logger.warning(f'CatForm errors: {cat_form.errors}')
            messages.error(request, 'لطفاً خطاهای فرم را برطرف کنید.')
            for err in image_errors:
                messages.error(request, err)

    else:
        form = AdForm(user=request.user, fixed_category=category)
        cat_form = build_category_form(category)

        # ═══ initial برند از URL ═══
        brand_from_url = request.GET.get('brand', '').strip()
        if brand_from_url:
            brand_key = f'{category.slug}__brand'
            for cf in category.get_category_fields():
                if cf.key == brand_key:
                    field_name = f'cf_{cf.pk}'
                    if field_name in cat_form.fields:
                        cat_form.fields[field_name].initial = brand_from_url
                    break

    return render(request, 'ad/ad_form.html', {
        'form': form,
        'cat_form': cat_form,
        'category': category,
    })
