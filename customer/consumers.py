# customer/consumers.py
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings

logger = logging.getLogger(__name__)


class CustomerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get user ID from the URL route
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.group_name = f'user_{self.user_id}'
        
        # Add to user-specific group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        
        # Only log in debug mode
        if settings.DEBUG:
            logger.info(f"Customer {self.user_id} connected to WebSocket")

    async def disconnect(self, close_code):
        # Remove from user-specific group
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        
        # Only log in debug mode
        if settings.DEBUG:
            logger.info(f"Customer {self.user_id} disconnected from WebSocket")

    async def order_update(self, event):
        """Handle order status updates for the customer"""
        # Only send important updates to customer frontend
        notification_type = event.get('notification_type', '')
        priority = event.get('priority', 'medium')
        
        # Filter out backend-only notifications to reduce frontend noise
        backend_only_types = [
            'preparation_started',
            'preparation_progress', 
            'internal_status_change',
            'restaurant_notification',
            'delivery_assignment',
            'ready_for_delivery'  # Customers don't need to know when order is ready for pickup
        ]
        
        # Only send critical notifications or high priority ones
        if notification_type not in backend_only_types and (
            priority in ['high', 'critical'] or 
            notification_type in ['payment_confirmed', 'delivery_accepted', 'out_for_delivery', 'delivery_completed', 'order_cancelled']
        ):
            await self.send(text_data=json.dumps(event))
            
            # Log only critical events in production
            if settings.DEBUG or notification_type in ['delivery_completed', 'order_cancelled', 'payment_failed']:
                logger.info(f"Sent order update to customer {self.user_id}: {notification_type}")

    async def delivery_update(self, event):
        """Handle delivery-specific updates"""
        # Only send high-priority delivery updates
        notification_type = event.get('notification_type', '')
        
        if notification_type in ['delivery_accepted', 'out_for_delivery', 'delivery_completed']:
            await self.send(text_data=json.dumps(event))
            
            if settings.DEBUG:
                logger.info(f"Sent delivery update to customer {self.user_id}: {notification_type}")

    async def payment_update(self, event):
        """Handle payment status updates"""
        await self.send(text_data=json.dumps(event))
        
        # Always log payment events for audit purposes
        logger.info(f"Sent payment update to customer {self.user_id}: {event.get('notification_type', 'unknown')}")

    async def general_notification(self, event):
        """Handle general notifications"""
        # Only send high-priority general notifications
        priority = event.get('priority', 'medium')
        
        if priority in ['high', 'critical']:
            await self.send(text_data=json.dumps(event))
            
            if settings.DEBUG:
                logger.info(f"Sent notification to customer {self.user_id}: {event.get('message', 'No message')}")