# delivery/consumers.py
import json
import logging
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)

class DeliveryConsumer(WebsocketConsumer):
    def connect(self):
        self.delivery_group_name = 'delivery_notifications'
        self.order_updates_group_name = 'order_updates'
        
        # Add to delivery_notifications group
        async_to_sync(self.channel_layer.group_add)(
            self.delivery_group_name,
            self.channel_name,
        )
        
        # Add to order_updates group
        async_to_sync(self.channel_layer.group_add)(
            self.order_updates_group_name,
            self.channel_name,
        )
        
        # Define group_name for disconnect method
        self.group_name = self.delivery_group_name
        
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

    def send_notification(self, event):
        message = event['message']
        self.send(text_data=json.dumps({
            'message': message
        }))
        
    def send_order_data(self, event):
        logger.info('Received event: %s', event)  # Log the entire event
        data = event.get('order', None)
        if data is None:
            logger.error('Order data is missing in the event: %s', event)
        else:
            logger.info('Sending order data: %s', data)
            self.send(text_data=json.dumps({
                'order': data
            }))