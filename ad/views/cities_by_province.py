from django.http import JsonResponse

from location.models import City


def cities_by_province(request):
    province_id = request.GET.get('province_id')
    if not province_id:
        return JsonResponse([], safe=False)
    data = list(City.objects.filter(province_id=province_id).values('id', 'name'))
    return JsonResponse(data, safe=False)
