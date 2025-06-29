# customer/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/customer/(?P<user_id>\d+)/$', consumers.CustomerConsumer.as_asgi()),
]
