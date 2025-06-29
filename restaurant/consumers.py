# restaurant/consumers.py
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings

logger = logging.getLogger(__name__)


class RestaurantConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.restaurant_id = self.scope['url_route']['kwargs']['restaurant_id']
        self.group_name = f'restaurant_{self.restaurant_id}'
        
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        
        if settings.DEBUG:
            logger.info(f"Restaurant {self.restaurant_id} connected to WebSocket")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        
        if settings.DEBUG:
            logger.info(f"Restaurant {self.restaurant_id} disconnected from WebSocket")

    async def order_update(self, event):
        await self.send(text_data=json.dumps(event))
        
        # Log only high-priority events in production
        if settings.DEBUG or event.get("priority") == "high":
            logger.info(f"Sent order update to restaurant {self.restaurant_id}: {event.get('notification_type', 'unknown')}")

    async def new_order(self, event):
        await self.send(text_data=json.dumps(event))
        
        # Always log new orders for business tracking
        if settings.DEBUG:
            logger.info(f"New order notification sent to restaurant {self.restaurant_id}")