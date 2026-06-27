from django.urls import path,include


app_name = 'ad'

urlpatterns = [
    path('api/v1/', include('ad.api.v1.urls')),
]