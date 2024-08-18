# restaurant/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import async_to_sync


class RestaurantConsumer(AsyncWebsocketConsumer):
    def connect(self):
        self.group_name = f'restaurant_{self.scope["user"].id}'
        async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)
        (self.group_name,
         self.channel_name
        )

    def order_update(self, event):
        self.send(text_data=json.dumps(event))

    def new_order(self, event):
        self.send(text_data=json.dumps(event))