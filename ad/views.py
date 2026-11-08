from django.shortcuts import render, redirect, reverse, get_object_or_404

from django.db.models import Q
from django.shortcuts import render

from .models import Ad,Category
from location.models import Province, City
from urllib.parse import urlencode, urlparse, parse_qs, urlunparse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
import json


def _get_city_slugs(request):
    """شهرها فقط از URL — بدون session."""
    return request.GET.getlist('cities')


def index(request):
    city_slugs = _get_city_slugs(request)

    # ۱ شهر از صفحه اصلی → /city/<slug>/
    if len(city_slugs) == 1 and request.path == '/':
        return redirect('ad:city-ads', slug=city_slugs[0])

    ads = Ad.objects.filter(status=Ad.Status.PUBLISHED)
    if city_slugs:
        ads = ads.filter(city__slug__in=city_slugs)
    ads = ads.select_related('province', 'city', 'category').order_by('-published_at')


    special_categories = Category.objects.filter(is_special=True).select_related('parent')
    context = {
        'ads': ads,
        'special_categories': special_categories,
    }
    return render(request, 'ad/index.html', context)


def cities_ads(request):
    city_slugs = request.GET.getlist('cities')  # ['tehran', 'shiraz']

    if len(city_slugs) == 1:
        return redirect('ad:city-ads', slug=city_slugs[0])

    ads = Ad.objects.filter(status=Ad.Status.PUBLISHED)
    if city_slugs:
        ads = ads.filter(city__slug__in=city_slugs)

    ads = ads.select_related('province', 'city', 'category').order_by('-published_at')

    return render(request, 'ad/cities_ad_list.html', {
        'ads': ads,
        'selected_cities': city_slugs,
    })


def city_ads(request, slug):
    city = get_object_or_404(City, slug=slug)

    ads = Ad.objects.filter(
        status=Ad.Status.PUBLISHED, city=city
    ).select_related('province', 'city', 'category').order_by('-published_at')

    return render(request, 'ad/city_ad_list.html', {'ads': ads, 'current_city': city})


def city_select(request):
    """فرم مودال اینجا submit می‌شه."""
    cities = request.GET.getlist('cities')  # ['tehran', 'shiraz']
    next_url = request.GET.get('next', '/')

    # اعتبارسنجی next
    if not next_url.startswith('/'):
        next_url = '/'

    # ۱ شهر → /city/<slug>/
    if len(cities) == 1:
        return redirect('ad:city-ads', slug=cities[0])

    # چند شهر → /cities/?cities=a&cities=b
    if len(cities) > 1:
        query = '&'.join(f'cities={c}' for c in cities)
        return redirect(f'/cities/?{query}')

    # بدون شهر
    return redirect(next_url)
# from urllib.parse import quote


# def city_select(request):
#     cities = request.GET.getlist('cities')
#
#     if len(cities) == 1:
#         return redirect('ad:city-ads', slug=cities[0])
#
#     if len(cities) > 1:
#         qs = '&'.join(f'cities={quote(c)}' for c in cities)
#         return redirect(f'/?{qs}')
#
#     return redirect('/')


def ad_detail(request, ad_id):
    ad = get_object_or_404(
        Ad.objects.select_related('category', 'province', 'city', 'neighborhood', 'user')
                  .prefetch_related('gallery', 'ad_attributes__category_field'),
        id=ad_id,
    )
    # افزایش بازدید
    Ad.objects.filter(pk=ad.pk).update(views_count=ad.views_count + 1)
    return render(request, 'ad/ad_detail.html', {'ad': ad})


from django.shortcuts import render, redirect
from .models import Category, CategoryField


ICON_MAP = {
    'apartment-sale': 'fa-building',
    'apartment-rent': 'fa-building',
    'house-villa-sale': 'fa-home',
    'house-villa-rent': 'fa-home',
    'land-old-building-sale': 'fa-map-marked-alt',
    'short-term-rent': 'fa-bed',
    'office-sale': 'fa-briefcase',
    'office-rent': 'fa-briefcase',
    'shop-sale': 'fa-store',
    'shop-rent': 'fa-store',
    'stall-sale': 'fa-shopping-basket',
    'stall-rent': 'fa-shopping-basket',
    'industrial-sale': 'fa-industry',
    'industrial-rent': 'fa-industry',
    'agricultural-sale': 'fa-seedling',
    'agricultural-rent': 'fa-seedling',
    'pre-sale': 'fa-key',
    'construction-partnership': 'fa-hard-hat',
}


from urllib.parse import quote
from django.urls import reverse

import json
from urllib.parse import quote
from django.urls import reverse


def choose_category(request):
    if request.method == 'POST':
        category_slug = request.POST.get('category', '').strip()
        brand = request.POST.get('brand', '').strip()

        if category_slug:
            url = reverse('ad:ad-create', kwargs={'category_slug': category_slug})
            if brand:
                url += '?brand=' + quote(brand)
            return redirect(url)
        return redirect('ad:choose-category')

    cat_ids_with_fields = (
        CategoryField.objects
        .values_list('category_id', flat=True)
        .distinct()
    )
    leaf_categories = (
        Category.objects
        .filter(id__in=cat_ids_with_fields, children__isnull=True)
        .select_related('parent', 'parent__parent')
        .order_by('title')
    )

    groups = {}
    for cat in leaf_categories:
        parent = cat.parent
        key = parent.id if parent else 0
        if key not in groups:
            groups[key] = {'parent': parent, 'children': []}

        cat.icon = ICON_MAP.get(cat.slug, 'fa-tag')

        # ═══ استخراج برندها از فیلد brand ═══
        brand_key = f'{cat.slug}__brand'
        brand_field = cat.get_category_fields().filter(key=brand_key).first()

        cat.brands = []
        cat.has_brands = False

        if brand_field and isinstance(brand_field.data, dict):
            models_map = brand_field.data.get('models') or {}
            options_list = brand_field.data.get('options') or []

            if models_map:
                cat.brands = list(models_map.keys())
            elif options_list:
                cat.brands = list(options_list)

            cat.has_brands = bool(cat.brands)

        # ═══ مهم: این خط رو اضافه کن ═══
        cat.brands_json = json.dumps(cat.brands, ensure_ascii=False) if cat.brands else '[]'

        groups[key]['children'].append(cat)

    grouped_categories = sorted(
        groups.values(),
        key=lambda g: g['parent'].title if g['parent'] else '',
    )

    return render(request, 'ad/choose_category.html', {
        'grouped_categories': grouped_categories,
    })


import io
import logging

from PIL import Image, ImageOps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from location.models import City, Neighborhood
from .models import Ad, Category, Gallery
from .forms import (
    AdForm, build_category_form, save_category_attributes,
    validate_image, MAX_IMAGES,
)

logger = logging.getLogger(__name__)


def cities_by_province(request):
    province_id = request.GET.get('province_id')
    if not province_id:
        return JsonResponse([], safe=False)
    data = list(City.objects.filter(province_id=province_id).values('id', 'name'))
    return JsonResponse(data, safe=False)


def neighborhoods_by_city(request):
    city_id = request.GET.get('city_id')
    if not city_id:
        return JsonResponse([], safe=False)
    data = list(Neighborhood.objects.filter(city_id=city_id).values('id', 'name'))
    return JsonResponse(data, safe=False)


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
                return redirect('ad:index')
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