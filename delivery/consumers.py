# delivery/consumers.py
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings

logger = logging.getLogger(__name__)


class DeliveryConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.delivery_group_name = "delivery_notifications"
        self.order_updates_group_name = "order_updates"

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
        
        if settings.DEBUG:
            logger.info(f"Delivery person connected to WebSocket: {self.channel_name}")

    async def disconnect(self, close_code):
        if settings.DEBUG:
            logger.info(f"Delivery person disconnecting with close code: {close_code}, channel: {self.channel_name}")
        
        # Remove from both groups
        await self.channel_layer.group_discard(
            self.delivery_group_name, 
            self.channel_name
        )
        await self.channel_layer.group_discard(
            self.order_updates_group_name, 
            self.channel_name
        )

    async def send_notification(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))

    async def send_order_data(self, event):
        data = event.get("order", None)
        if data is None:
            if settings.DEBUG:
                logger.error("Order data is missing in the event: %s", event)
        else:
            if settings.DEBUG:
                logger.info("Sending order data: %s", data)
            await self.send(text_data=json.dumps({"order": data}))

    async def order_update(self, event):
        # Only send important order updates to reduce noise
        notification_type = event.get("notification_type", "")
        priority = event.get("priority", "medium")
        
        # Filter out non-essential notifications for delivery personnel
        if notification_type in ['new_order_available', 'order_cancelled', 'order_reassigned'] or priority == 'high':
            message = event.get("message", "Order status updated")
            order = event.get("order", {})

            await self.send(text_data=json.dumps({
                "type": "order_update",
                "message": message,
                "order": order,
                "notification_type": notification_type,
                "priority": priority
            }))
            
            # Log only important events in production
            if settings.DEBUG or priority == "high":
                logger.info("Sent order update to delivery: %s", notification_type)

    async def new_order(self, event):
        # Only log in debug mode
        if settings.DEBUG:
            logger.info("Received new order notification: %s", event)
        
        await self.send(
            text_data=json.dumps(
                {
                    "type": "new_order",
                    "message": event.get("message", "New order received"),
                    "order": event.get("order", {}),
                }
            )
        )
