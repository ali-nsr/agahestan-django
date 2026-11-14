from django.shortcuts import redirect
from ..models import Category
from location.models import City

def city_select(request):
    """مودال انتخاب شهر اینجا submit می‌شه."""
    cities = request.GET.getlist('cities')  # ?cities=tehran&cities=shiraz
    next_url = request.GET.get('next', '/iran/')

    # ─── تشخیص دسته از next_url ───
    category_slug = None
    path_parts = [
        p for p in next_url.split('?')[0].strip('/').split('/')
        if p and p != 'iran'
    ]
    if path_parts:
        last = path_parts[-1]
        if Category.objects.filter(slug=last, children__isnull=True).exists():
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

# def city_select(request):
#     """فرم مودال اینجا submit می‌شه."""
#     cities = request.GET.getlist('cities')  # ['tehran', 'shiraz']
#     next_url = request.GET.get('next', '/')
#
#     # اعتبارسنجی next
#     if not next_url.startswith('/'):
#         next_url = '/'
#
#     # ۱ شهر → /city/<slug>/
#     if len(cities) == 1:
#         return redirect('ad:city-ads', slug=cities[0])
#
#     # چند شهر → /cities/?cities=a&cities=b
#     if len(cities) > 1:
#         query = '&'.join(f'cities={c}' for c in cities)
#         return redirect(f'/cities/?{query}')
#
#     # بدون شهر
#     return redirect(next_url)
