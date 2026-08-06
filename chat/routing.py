# from django.urls import path
#
# from . import consumers
#
# websocket_urlpatterns = [
#     path('ws/chat/<str:chat_uuid>/', consumers.ChatConsumer.as_asgi()),
# ]
# chat/routing.py
# chat/routing.py
from django.urls import re_path

def get_websocket_urlpatterns():
    from . import consumers
    return [
        re_path(r'ws/chat/(?P&lt;room_name&gt;\w+)/$', consumers.ChatConsumer.as_asgi()),
    ]

websocket_urlpatterns = get_websocket_urlpatterns()
