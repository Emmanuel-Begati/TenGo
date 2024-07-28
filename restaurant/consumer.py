import json
from channels.generic.websocket import AsyncWebsocketConsumer

class RestaurantConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add('restaurant_notifications', self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard('restaurant_notifications', self.channel_name)

    async def send_notification(self, event):
        await self.send(text_data=json.dumps(event))