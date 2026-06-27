from django.urls import path

from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from . import views

app_name = 'api'

urlpatterns = [
    # auth
    path('auth/send-otp/', views.SendOTPView.as_view()),
    path('auth/verify-otp/', views.VerifyOTPView.as_view()),


    # profile
    path('user-profile/', views.ProfileApiView.as_view(), name='profile'),
    path('user-ads/', views.UserAdListAPIView.as_view(), name='user-ads'),
    path('user-ads/<str:uuid>/', views.UserAdRetrieveApiView.as_view(), name='user-ad-detail'),
    path('user-bookmarks/', views.UserBookmarksApiView.as_view(), name='bookmarks'),
    path('add-or-remove-bookmark/<int:ad_id>/', views.BookmarkApiView.as_view(), name='bookmark'),

    # login jwt
    path('jwt/create/', views.CustomTokenObtainPairView.as_view(), name='jwt-create'),
    path('jwt/refresh/', views.CustomTokenRefreshView.as_view(), name='jwt-refresh'),
    path('jwt/verify/', views.CustomTokenVerifyView.as_view(), name='jwt-verify'),
]
