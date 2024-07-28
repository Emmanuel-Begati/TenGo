from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/restaurant/', consumers.RestaurantConsumer.as_asgi()),
]