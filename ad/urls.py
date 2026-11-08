from django.urls import path, include

from . import views

app_name = 'ad'

urlpatterns = [
    path('', views.index, name='index'),
    path('city-select/', views.city_select, name='city-select'),
    path('city/<slug:slug>/', views.city_ads, name='city-ads'),
    path('cities/', views.cities_ads, name='cities-ads'),

    path('ad/<ad_id>/', views.ad_detail, name='ad-detail'),
    path('city-select/', views.city_select, name='city_select'),

    # جدید
    path('choose-category/', views.choose_category, name='choose-category'),
    path('create/<slug:category_slug>/', views.ad_create, name='ad-create'),
    # AJAX
    path('api/cities/', views.cities_by_province, name='cities-by-province'),
    path('api/neighborhoods/', views.neighborhoods_by_city, name='neighborhoods-by-city'),

    # api
    path('api/v1/', include('ad.api.v1.urls')),
]
