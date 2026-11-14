from django.shortcuts import render,redirect

from ad.models import Ad, Category
from core.models import Slider


def index(request):
    city_slugs = request.GET.getlist('cities')

    # ۱ شهر از صفحه اصلی → /city/<slug>/
    if len(city_slugs) == 1 and request.path == '/':
        return redirect('ad:city-ads', slug=city_slugs[0])

    # ads = Ad.objects.filter(status=Ad.Status.PUBLISHED)
    # if city_slugs:
    #     ads = ads.filter(city__slug__in=city_slugs)
    # ads = ads.select_related('province', 'city', 'category').order_by('published_at')

    special_categories = Category.objects.filter(is_special=True).select_related('parent')
    main_image = Slider.objects.get_main_image()
    banners = Slider.objects.get_banners()
    context = {
        # 'ads': ads,
        'special_categories': special_categories,
        'main_image': main_image,
        'banners': banners,
    }
    return render(request, 'ad/index/index.html', context)
