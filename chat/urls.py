from django.urls import path, include

from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_list, name='chat-list'),
    path('start/<uuid:ad_uuid>/', views.start_chat, name='start-chat'),
    path('<uuid:chat_uuid>/', views.chat_detail, name='chat-detail'),

    # api
    path('api/v1/', include('chat.api.v1.urls')),
]
