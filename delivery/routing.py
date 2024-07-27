# delivery/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path('ws/delivery/', consumers.DeliveryConsumer.as_asgi()),
]
