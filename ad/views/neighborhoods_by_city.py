from django.http import JsonResponse

from location.models import Neighborhood


def neighborhoods_by_city(request):
    city_id = request.GET.get('city_id')
    if not city_id:
        return JsonResponse([], safe=False)
    data = list(Neighborhood.objects.filter(city_id=city_id).values('id', 'name'))
    return JsonResponse(data, safe=False)
