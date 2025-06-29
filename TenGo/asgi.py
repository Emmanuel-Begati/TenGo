# TenGo/asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
import delivery.routing
import restaurant.routing
import customer.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TenGo.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                delivery.routing.websocket_urlpatterns + 
                restaurant.routing.websocket_urlpatterns +
                customer.routing.websocket_urlpatterns
            )
        )
    ),
})