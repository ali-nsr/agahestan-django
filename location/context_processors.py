# from location.models import Province, City
# from location.services import get_selected_cities
#
#
# def city_selector(request):
#     return {
#         'provinces': Province.objects.only('id', 'name'),
#         'cities': City.objects.only('id', 'name', 'slug', 'province_id').order_by('name'),
#         'selected_cities': get_selected_cities(request),
#     }

from location.models import Province, City
from location.services import handle_city_filter, SESSION_KEY


def city_selector(request):
    selected = request.GET.getlist('cities')
    return {
        'provinces': Province.objects.only('id', 'name'),
        'cities': City.objects.select_related('province')
                               .only('id', 'name', 'slug', 'province_id', 'province__name')
                               .order_by('province__name', 'name'),  # ← این خط
        'selected_cities': selected,
    }