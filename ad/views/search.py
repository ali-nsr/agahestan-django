from django.shortcuts import get_object_or_404,render
from django.db.models import Q
from .category_list import _base_qs,_get_cities,_get_descendant_ids,_context
from ..models import Category

def search(request):
    q = (request.GET.get('q') or '').strip()
    qs = _base_qs()

    # جستجو در عنوان، توضیحات، و نام شهر
    if q:
        qs = qs.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(city__name__icontains=q) |
            Q(province__name__icontains=q) |
            Q(neighborhood__name__icontains=q)
        )

    # فیلتر شهر
    selected_cities = _get_cities(request)
    if selected_cities:
        qs = qs.filter(city__slug__in=selected_cities)

    # فیلتر دسته (اگه از توی نتایج کلیک کرد)
    category_slug = request.GET.get('category')
    category = None
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        ids = _get_descendant_ids(category)
        qs = qs.filter(category_id__in=ids)

    qs = qs.order_by('-published_at').distinct()

    ctx = _context(qs, request, category=category, selected_cities=selected_cities)
    ctx['q'] = q
    ctx['page_title'] = f'نتایج جستجو برای «{q}»' if q else 'جستجو'

    return render(request, 'ad/search.html', ctx)