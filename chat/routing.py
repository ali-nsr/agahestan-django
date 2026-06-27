from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('ws/chat/<str:chat_uuid>/', consumers.ChatConsumer.as_asgi()),
]
