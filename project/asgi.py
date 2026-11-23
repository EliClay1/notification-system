"""
ASGI config for project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from channels.auth import AuthMiddleware
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from notifications.routing import websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

application = ProtocolTypeRouter(
    {
        "websocket": AuthMiddleware(URLRouter(websocket_urlpatterns)),
        "http": get_asgi_application(),
    }
)
