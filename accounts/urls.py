from django.urls import path, include

from . import views
from . import dashboards

app_name = 'accounts'

urlpatterns = [
    path('auth/login/', views.login, name='login'),
    path('auth/logout/', views.logout, name='logout'),
    # path('dashboard/', dashboards.dashboard, name='dashboard'),
    path('dashboard/ads/', dashboards.user_ads, name='dashboard'),
    path('dashboard/<uuid:uuid>/delete/', dashboards.ad_delete, name='ad-delete'),

    # api
    path('api/v1/', include('accounts.api.v1.urls')),
]
