from django.shortcuts import redirect
from location.models import City

SESSION_KEY = 'selected_cities'


def get_selected_cities(request):
    """
    شهرهای انتخاب‌شده کاربر رو برمی‌گردونه.
    اولویت: URL شهر تکی → query param → session
    """
    if hasattr(request, '_selected_cities'):
        return request._selected_cities

    # ۱. اگر توی /city-ads/<slug>/ هستیم
    city_slug_from_url = getattr(request, 'city_slug_from_url', None)
    if city_slug_from_url:
        city_slugs = [city_slug_from_url]
        request.session[SESSION_KEY] = city_slugs
        request._selected_cities = city_slugs
        return city_slugs

    # ۲. اگر ?cities=a&cities=b داریم
    city_slugs = request.GET.getlist('cities')
    if city_slugs:
        valid_slugs = set(
            City.objects.filter(slug__in=city_slugs).values_list('slug', flat=True)
        )
        city_slugs = [s for s in city_slugs if s in valid_slugs]
        request.session[SESSION_KEY] = city_slugs
    else:
        # ۳. از session
        city_slugs = request.session.get(SESSION_KEY, [])

    request._selected_cities = city_slugs
    return city_slugs


def set_selected_cities(request, city_slugs):
    request.session[SESSION_KEY] = list(city_slugs)


def clear_selected_cities(request):
    request.session.pop(SESSION_KEY, None)

def redirect_if_single_city(request):
    """
    اگر ?cities=<slug> دقیقاً یک شهر بود، به /city/<slug>/ redirect کن.
    در غیر این صورت None برمی‌گردونه.
    فقط برای صفحات لیست (index, cities_ads, search, category, ...) صدا بزن.
    """
    city_slugs = request.GET.getlist('cities')
    if len(city_slugs) == 1:
        return redirect('ad:city-ads', slug=city_slugs[0])
    return None

from django.shortcuts import redirect
from location.models import City

SESSION_KEY = 'selected_cities'


def handle_city_filter(request):
    """
    همه منطق شهر اینجاست:
    - شهرهای انتخاب‌شده رو برمی‌گردونه (از ?cities= یا session)
    - اگه ?cities= یک شهر بود و توی صفحه اصلی بودیم → redirect به /city/<slug>/
    - اگه ?cities= بود → ذخیره در session
    """
    city_slugs = request.GET.getlist('cities')

    # ?cities= یک شهر از صفحه اصلی → /city/<slug>/
    if len(city_slugs) == 1 and request.path in ('/', '/cities/'):
        request.session[SESSION_KEY] = city_slugs
        return redirect('ad:city-ads', slug=city_slugs[0])

    # ?cities= بود → ذخیره در session
    if city_slugs:
        valid = set(
            City.objects.filter(slug__in=city_slugs).values_list('slug', flat=True)
        )
        city_slugs = [s for s in city_slugs if s in valid]
        request.session[SESSION_KEY] = city_slugs
    else:
        city_slugs = request.session.get(SESSION_KEY, [])

    return city_slugs  # یا QuerySet شهرها یا redirect


def clear_cities(request):
    request.session.pop(SESSION_KEY, None)
    return redirect(request.META.get('HTTP_REFERER', '/'))