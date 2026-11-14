from django.urls import path, re_path

from . import consumers

websocket_urlpatterns = [
    path('ws/chat/<str:chat_uuid>/', consumers.ChatConsumer.as_asgi()),
    path('ws/notifications/', consumers.NotificationConsumer.as_asgi()),
]

# websocket_urlpatterns = [
#     re_path(r'^ws/chat/(?P<chat_uuid>[^/]+)/$', consumers.ChatConsumer.as_asgi()),
#     re_path(r'^ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
# ]

# chat/routing.py
# from django.urls import re_path
#
# def get_websocket_urlpatterns():
#     from . import consumers
#     return [
#         re_path(r'ws/chat/(?P&lt;room_name&gt;\w+)/$', consumers.ChatConsumer.as_asgi()),
#     ]
#
# websocket_urlpatterns = get_websocket_urlpatterns()
