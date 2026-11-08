from django.urls import path, include

from . import views
from . import dashboards

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login, name='login'),
    path('dashboard/', dashboards.dashboard, name='dashboard'),

    # api
    path('api/v1/', include('accounts.api.v1.urls')),
]