# import os
# import django
# from django.core.asgi import get_asgi_application
# from channels.auth import AuthMiddlewareStack
# from channels.routing import ProtocolTypeRouter, URLRouter
# from chat import routing
#
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
# django.setup()
#
# application = ProtocolTypeRouter({
#     'http': get_asgi_application(),
#     'websocket': AuthMiddlewareStack(
#         URLRouter(routing.websocket_urlpatterns)
#     ),
# })
# config/asgi.py
# import os
# from django.core.asgi import get_asgi_application
#
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
#
# # اول Django را initialize کنید
# django_asgi_app = get_asgi_application()
#
# # سپس import channels
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# from chat.routing import websocket_urlpatterns
#
# application = ProtocolTypeRouter({
#     'http': django_asgi_app,
#     'websocket': AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
# })

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_asgi_application()
