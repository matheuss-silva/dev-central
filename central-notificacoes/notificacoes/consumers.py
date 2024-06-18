import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Notification
from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger(__name__)

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_authenticated:
            self.user_id = str(self.scope["user"].id)
            self.room_group_name = f'notifications_{self.user_id}'

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()
        else:
            print("ERROOOOo")
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json.get('action')

        if action == 'fetch_notifications':
            notifications = await self.fetch_notifications()
            await self.send(text_data=json.dumps({
                'notifications': notifications
            }))
            
    async def notify(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))


    @database_sync_to_async
    def fetch_notifications(self):
        logger.debug(f"Querying unread notifications for user {self.user_id}")
        notifications = Notification.objects.filter(recipient=self.user, read=False)
        return list(notifications.values())
