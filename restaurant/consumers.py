# restaurant/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class RestaurantConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.restaurant_id = self.scope['url_route']['kwargs']['restaurant_id']
        self.group_name = f'restaurant_{self.restaurant_id}'
        
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def order_update(self, event):
        print(f"Sending event: {event}")  # for debugging
        await self.send(text_data=json.dumps(event))


    async def new_order(self, event):
        await self.send(text_data=json.dumps(event))