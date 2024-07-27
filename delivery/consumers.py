# delivery/consumers.py
import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

class DeliveryConsumer(WebsocketConsumer):
    def connect(self):
        self.group_name = 'delivery_notifications'
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)
        self.send(text_data=json.dumps({
            'message': 'Received your message!'
        }))

    def send_notification(self, event):
        message = event['message']
        self.send(text_data=json.dumps({
            'message': message
        }))
