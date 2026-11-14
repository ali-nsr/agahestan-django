from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Count
from location.models import City
from ..models import Ad, Category


def _base_qs():
    return Ad.objects.filter(
        status=Ad.Status.PUBLISHED
    ).select_related('category', 'province', 'city', 'neighborhood', 'user')


def _get_cities(request):
    raw = request.GET.getlist('cities')
    result = []
    for v in raw:
        result.extend([x.strip() for x in v.split(',') if x.strip()])
    return result


def _get_descendant_ids(category):
    """ID دسته + همه‌ی فرزندانش در هر سطح."""
    ids = [category.id]
    to_process = [category.id]
    while to_process:
        children = list(
            Category.objects.filter(parent_id__in=to_process)
            .values_list('id', flat=True)
        )
        if not children:
            break
        ids.extend(children)
        to_process = children
    return ids


def _apply_fields(qs, request, category):
    if not category:
        return qs

    for cf in category.get_category_fields():
        value = request.GET.get(cf.key, '').strip()
        if not value:
            continue

        if cf.type == cf.FieldType.BOOLEAN:
            if value in ('1', 'true'):
                qs = qs.filter(
                    ad_attributes__category_field=cf,
                    ad_attributes__value__in=['True', 'true', '1'],
                )
        elif cf.type == cf.FieldType.MULTI_CHOICE:
            qs = qs.filter(
                ad_attributes__category_field=cf,
                ad_attributes__value__icontains=value,
            )
        else:
            qs = qs.filter(
                ad_attributes__category_field=cf,
                ad_attributes__value=value,
            )

    return qs.distinct()


def _context(qs, request, category=None, city=None, selected_cities=None):
    paginator = Paginator(qs, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    cat_fields = category.get_category_fields() if category else []

    return {
        'ads': page_obj,
        'page_obj': page_obj,
        'category': category,
        'city': city,
        'selected_cities': selected_cities or [],
        'cat_fields': cat_fields,
        'total_count': paginator.count,
    }


def iran_landing(request, category_slug=None):
    qs = _base_qs()

    category = None
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)

        # همه‌ی آگهی‌های خود دسته + همه فرزندان
        descendant_ids = _get_descendant_ids(category)
        qs = qs.filter(category_id__in=descendant_ids)

    selected_cities = _get_cities(request)
    if selected_cities:
        qs = qs.filter(city__slug__in=selected_cities)

    qs = _apply_fields(qs, request, category).order_by('-published_at')

    ctx = _context(qs, request, category, None, selected_cities)
    ctx['page_title'] = (
        f'{category.title} در سراسر ایران' if category
        else 'آگهی‌ها در سراسر ایران'
    )

    if category_slug is None and not selected_cities:
        return render(request, 'ad/index/index.html', ctx)
    return render(request, 'ad/landing_page.html', ctx)


def city_landing(request, city_slug, category_slug=None):
    city = get_object_or_404(City, slug=city_slug)
    qs = _base_qs().filter(city=city)

    category = None
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)

        descendant_ids = _get_descendant_ids(category)
        qs = qs.filter(category_id__in=descendant_ids)

    qs = _apply_fields(qs, request, category).order_by('-published_at')

    ctx = _context(qs, request, category, city, [city.slug])
    ctx['page_title'] = (
        f'{category.title} در {city.name}' if category
        else f'آگهی‌های {city.name}'
    )
    return render(request, 'ad/landing_page.html', ctx)


def city_select(request):
    cities = request.GET.getlist('cities')
    next_url = request.GET.get('next', '/iran/')

    # ─── تشخیص category از next_url ───
    category_slug = None
    path_parts = [
        p for p in next_url.split('?')[0].strip('/').split('/')
        if p and p != 'iran'
    ]
    if path_parts:
        last = path_parts[-1]
        if Category.objects.filter(slug=last).exists():
            category_slug = last

    # ─── اعتبارسنجی شهرها ───
    valid = set(
        City.objects.filter(slug__in=cities).values_list('slug', flat=True)
    )
    cities = [c for c in cities if c in valid]

    # ─── بدون شهر ───
    if not cities:
        if category_slug:
            return redirect('ad:iran-category-landing', category_slug=category_slug)
        return redirect('ad:iran-landing')

    # ─── تک‌شهر ───
    if len(cities) == 1:
        if category_slug:
            return redirect(
                'ad:city-category-landing',
                city_slug=cities[0],
                category_slug=category_slug,
            )
        return redirect('ad:city-landing', city_slug=cities[0])

    # ─── چند شهر ───
    query = ','.join(cities)
    if category_slug:
        return redirect(f'/iran/{category_slug}/?cities={query}')
    return redirect(f'/iran/?cities={query}')