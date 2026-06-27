from django.urls import path

from . import views


urlpatterns = [
    path('user-chats/', views.ChatListAPIView.as_view()),
    path('create/<ad_id>/', views.ChatCreateAPIView.as_view()),
    path('chat/<chat_uuid>/', views.ChatMessageAPIView.as_view()),
]
