"""
ASGI config for DRF_useFul_Components project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

# import os
#
# from django.core.asgi import get_asgi_application
#
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DRF_useFul_Components.settings')
#
# application = get_asgi_application()



import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from channels_app.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DRF_useFul_Components.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # HTTP 协议仍然由 Django 处理
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)  # WebSocket 的路由
    ),
})
