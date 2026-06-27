from django.urls import path

from . import views

urlpatterns = [
    path('provinces/', views.ProvinceListAPIView.as_view()),
    path('provinces/<pk>/', views.ProvinceRetrieveAPIView.as_view()),
    path('cities/', views.CityListAPIView.as_view()),
    path('cities/<pk>/', views.CityRetrieveAPIView.as_view()),
    path('neighborhoods/', views.NeighborhoodListAPIView.as_view()),
    path('neighborhoods/<pk>/', views.NeighborhoodRetrieveAPIView.as_view()),
]
