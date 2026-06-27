from django.urls import path

from . import views

app_name = 'api'

urlpatterns = [
    path('follow/<user_id>/', views.FollowUserApiView.as_view(), name='follow'),
    path('ads/<user_id>/', views.UserAdsApiView.as_view(), name='user-ads'),
]
