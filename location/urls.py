from django.urls import path, include

from . import views

app_name = 'location'

urlpatterns = [
    path('clear-cities/', views.clear_cities, name='clear_cities'),
    path('api/v1/', include('location.api.v1.urls')),
]
