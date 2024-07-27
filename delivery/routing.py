# delivery/routing.py
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/delivery/', consumers.DeliveryConsumer.as_asgi()),
]
