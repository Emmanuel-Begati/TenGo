from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/restaurant/(?P<id>\d+)/$', consumers.RestaurantConsumer.as_asgi()),
]