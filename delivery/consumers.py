# delivery/consumers.py
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)

class DeliveryConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.delivery_group_name = 'delivery_notifications'
        self.order_updates_group_name = 'order_updates'
        
        # Add to delivery_notifications group
        await self.channel_layer.group_add(
            self.delivery_group_name,
            self.channel_name,
        )
        
        # Add to order_updates group
        await self.channel_layer.group_add(
            self.order_updates_group_name,
            self.channel_name,
        )
        
        # Define group_name for disconnect method
        self.group_name = self.delivery_group_name
        
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_notification(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))
        
    async def send_order_data(self, event):
        logger.info('Received event: %s', event)  # Log the entire event
        data = event.get('order', None)
        if data is None:
            logger.error('Order data is missing in the event: %s', event)
        else:
            logger.info('Sending order data: %s', data)
            await self.send(text_data=json.dumps({
                'order': data
            }))
    
    async def order_update(self, event):
        await self.send(text_data=json.dumps(event))

    async def new_order(self, event):
        await self.send(text_data=json.dumps(event))