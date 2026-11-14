from django.shortcuts import redirect,reverse
from django.core.cache import cache

from .models import Ad,Category
from location.models import Province, City
# from core.filters import CitySelectForm


def core_context(request):

    # neighborhoods_filter= NeighborhoodFilter(request.GET, queryset=Neighborhood.objects.all()),
    # print(request.GET.getlist('states[]'))
    # print(list(map(int, request.GET.getlist('states[]'))))
    # print(len(list(map(int, request.GET.getlist('states[]')))))
    city_slugs = request.GET.getlist('cities')  # ?cities=tehran&cities=karaj

    # برای پر کردن Select2
    provinces = Province.objects.only('id', 'name')
    cities = City.objects.only('id', 'name', 'slug', 'province_id').order_by('name')

    context = {
        'provinces': provinces,
        'cities': cities,
        'selected_cities': city_slugs,  # برای نگه‌داشتن انتخاب‌ها بعد از submit
    }
    return context


    # return {
    #     'provinces': Province.objects.all(),
    #     # 'neighborhoods_filter': neighborhoods_filter,
    #     # 'cities_form': CitySelectForm(),
    #     # 'states':list(map(int, request.GET.getlist('states'))),
    #     # 'states_count':len(list(map(int, request.GET.getlist('states')))),
    # }


def header_categories(request):
    cache_key = 'header_categories'
    categories_tree = cache.get(cache_key)
    if categories_tree is None:
        categories_tree = Category.objects.get_all_categories()
        cache.set(cache_key, categories_tree, 28800)
    return {
        'header_categories': categories_tree
    }

def menu_categories(request):
    return {
        'parent_categories': Category.objects.filter(
            parent__isnull=True
        ).prefetch_related('children').order_by('title'),
    }