from django.urls import path,include

app_name = 'social'

urlpatterns = [
    path('api/v1/', include('social.api.v1.urls')),
]
