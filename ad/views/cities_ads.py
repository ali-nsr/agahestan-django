from django.shortcuts import render

from ad.models import Ad, Category
from django.shortcuts import redirect


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
