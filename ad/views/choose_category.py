from django.shortcuts import render, redirect
from django.urls import reverse
from urllib.parse import quote
import json

from ad.models import Category, CategoryField


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
    'vehicles-cars-sedan': 'fa-car',
    'vehicles-cars-pickup': 'fa-truck-pickup',
    'vehicles-cars-classic': 'fa-car-side',
    'vehicles-motorcycles': 'fa-motorcycle',
    'vehicles-heavy-trucks': 'fa-truck',
    'vehicles-heavy-agricultural': 'fa-tractor',
    'vehicles-rental': 'fa-key',
    'vehicles-spare-parts-components': 'fa-cog',
    'vehicles-spare-parts-accessories': 'fa-tools',
    'vehicles-boats-others': 'fa-ship',
}


def _get_icon(cat):
    if cat.slug in ICON_MAP:
        return ICON_MAP[cat.slug]

    if cat.parent:
        parent_icons = {
            'vehicles-cars-sedan': 'fa-car',
            'vehicles-cars-pickup': 'fa-truck-pickup',
            'vehicles-cars-classic': 'fa-car-side',
            'vehicles-motorcycles': 'fa-motorcycle',
            'vehicles-heavy-trucks': 'fa-truck',
            'vehicles-rental': 'fa-key',
        }
        if cat.parent.slug in parent_icons:
            return parent_icons[cat.parent.slug]

    return 'fa-tag'


def choose_category(request):
    if request.method == 'POST':
        category_slug = request.POST.get('category', '').strip()
        if category_slug:
            return redirect('ad:ad-create', category_slug=category_slug)
        return redirect('ad:choose-category')

    leaf_ids = (
        CategoryField.objects
        .values_list('category_id', flat=True)
        .distinct()
    )

    leaves = (
        Category.objects
        .filter(id__in=leaf_ids, children__isnull=True)
        .select_related('parent', 'parent__parent')
        .order_by('title')
    )

    items = []
    for leaf in leaves:
        path = []
        node = leaf
        while node:
            path.insert(0, {'slug': node.slug, 'title': node.title})
            node = node.parent

        items.append({
            'slug': leaf.slug,
            'title': leaf.title,
            'path': path,
        })

    return render(request, 'ad/choose_category.html', {
        'items_json': json.dumps(items, ensure_ascii=False),
    })


# def choose_category(request):
#     if request.method == 'POST':
#         category_slug = request.POST.get('category', '').strip()
#         brand = request.POST.get('brand', '').strip()
#
#         if category_slug:
#             url = reverse('ad:ad-create', kwargs={'category_slug': category_slug})
#             if brand:
#                 url += '?brand=' + quote(brand)
#             return redirect(url)
#         return redirect('ad:choose-category')
#
#     cat_ids_with_fields = (
#         CategoryField.objects
#         .values_list('category_id', flat=True)
#         .distinct()
#     )
#     leaf_categories = (
#         Category.objects
#         .filter(id__in=cat_ids_with_fields, children__isnull=True)
#         .select_related('parent', 'parent__parent')
#         .order_by('title')
#     )
#
#     groups = {}
#     for cat in leaf_categories:
#         parent = cat.parent
#         key = parent.id if parent else 0
#         if key not in groups:
#             groups[key] = {'parent': parent, 'children': []}
#
#         cat.icon = ICON_MAP.get(cat.slug, 'fa-tag')
#
#         # ═══ استخراج برندها از فیلد brand ═══
#         brand_key = f'{cat.slug}__brand'
#         brand_field = cat.get_category_fields().filter(key=brand_key).first()
#
#         cat.brands = []
#         cat.has_brands = False
#
#         if brand_field and isinstance(brand_field.data, dict):
#             models_map = brand_field.data.get('models') or {}
#             options_list = brand_field.data.get('options') or []
#
#             if models_map:
#                 cat.brands = list(models_map.keys())
#             elif options_list:
#                 cat.brands = list(options_list)
#
#             cat.has_brands = bool(cat.brands)
#
#         # ═══ مهم: این خط رو اضافه کن ═══
#         cat.brands_json = json.dumps(cat.brands, ensure_ascii=False) if cat.brands else '[]'
#
#         groups[key]['children'].append(cat)
#
#     grouped_categories = sorted(
#         groups.values(),
#         key=lambda g: g['parent'].title if g['parent'] else '',
#     )
#
#     return render(request, 'ad/choose_category.html', {
#         'grouped_categories': grouped_categories,
#     })
# def choose_category(request):
#     if request.method == 'POST':
#         category_slug = request.POST.get('category', '').strip()
#         if category_slug:
#             return redirect('ad:ad-create', category_slug=category_slug)
#         return redirect('ad:choose-category')
#
#     cat_ids = CategoryField.objects.values_list('category_id', flat=True).distinct()
#
#     leaf_categories = (
#         Category.objects
#         .filter(id__in=cat_ids, children__isnull=True)
#         .select_related('parent')
#         .order_by('title')
#     )
#
#     groups = {}
#     for cat in leaf_categories:
#         parent = cat.parent
#         key = parent.id if parent else 0
#         if key not in groups:
#             groups[key] = {'parent': parent, 'children': []}
#         cat.icon = ICON_MAP.get(cat.slug, 'fa-tag')
#         groups[key]['children'].append(cat)
#
#     grouped_categories = sorted(
#         groups.values(),
#         key=lambda g: g['parent'].title if g['parent'] else '',
#     )
#
#     return render(request, 'ad/choose_category.html', {
#         'grouped_categories': grouped_categories,
#     })