from django.shortcuts import get_object_or_404
from django.shortcuts import render

from ad.models import Ad
from location.models import City


def city_ads(request, slug):
    city = get_object_or_404(City, slug=slug)

    ads = Ad.objects.filter(
        status=Ad.Status.PUBLISHED, city=city
    ).select_related('province', 'city', 'category').order_by('-published_at')

    return render(request, 'ad/city_ad_list.html', {'ads': ads, 'current_city': city})
