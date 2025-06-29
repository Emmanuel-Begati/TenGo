# customer/consumers.py
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class CustomerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get user ID from the URL route
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.group_name = f'user_{self.user_id}'
        
        # Add to user-specific group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        logger.info(f"Customer {self.user_id} connected to WebSocket")

    async def disconnect(self, close_code):
        # Remove from user-specific group
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        logger.info(f"Customer {self.user_id} disconnected from WebSocket")

    async def order_update(self, event):
        """Handle order status updates for the customer"""
        logger.info(f"Sending order update to customer {self.user_id}: {event}")
        await self.send(text_data=json.dumps(event))

    async def delivery_update(self, event):
        """Handle delivery-specific updates"""
        logger.info(f"Sending delivery update to customer {self.user_id}: {event}")
        await self.send(text_data=json.dumps(event))

    async def payment_update(self, event):
        """Handle payment status updates"""
        logger.info(f"Sending payment update to customer {self.user_id}: {event}")
        await self.send(text_data=json.dumps(event))

    async def general_notification(self, event):
        """Handle general notifications"""
        logger.info(f"Sending notification to customer {self.user_id}: {event}")
        await self.send(text_data=json.dumps(event))
