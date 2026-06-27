from django.urls import path, include

app_name = 'location'

urlpatterns = [
    path('api/v1/', include('location.api.v1.urls')),
]
