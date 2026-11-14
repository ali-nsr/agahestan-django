from django.urls import path, include
from django.views.generic import RedirectView
from . import views

app_name = 'ad'

urlpatterns = [
    # ═══ ۱. ریشه → /iran/ ═══
    path('', RedirectView.as_view(pattern_name='ad:iran-landing', permanent=False)),

    # ═══ ۲. API ═══
    path('api/v1/', include('ad.api.v1.urls')),
    path('api/cities/', views.cities_by_province, name='cities-by-province'),
    path('api/neighborhoods/', views.neighborhoods_by_city, name='neighborhoods-by-city'),

    # ═══ ۳. مسیرهای خاص (قبل از <slug>/<slug>/) ═══
    path('city-select/', views.city_select, name='city-select'),
    path('choose-category/', views.choose_category, name='choose-category'),
    path('create/<slug:category_slug>/', views.ad_create, name='ad-create'),
    path('ad/<uuid>/', views.ad_detail, name='ad-detail'),
    path('<uuid:uuid>/edit/', views.ad_edit, name='ad-edit'),

    # URLهای قدیمی (برای سازگاری — می‌تونی بعداً حذف کنی)
    path('city/<slug:slug>/', views.city_ads, name='city-ads'),
    path('cities/', views.cities_ads, name='cities-ads'),

    # ═══ ۴. Iran ═══
    path('iran/', views.iran_landing, name='iran-landing'),
    path('iran/<slug:category_slug>/', views.iran_landing, name='iran-category-landing'),

    # ═══ ۵. شهر + دسته ═══
    path('city/<slug:city_slug>/<slug:category_slug>/',
         views.city_landing, name='city-category-landing'),

    # ═══ ۶. فقط شهر (آخر — catch-all) ═══
    path('city/<slug:city_slug>/', views.city_landing, name='city-landing'),
]