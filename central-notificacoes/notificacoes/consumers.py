import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Notification

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
            logger.info(f'User {self.user_id} connected to group {self.room_group_name}')
        else:
            await self.close()
            logger.warning('Anonymous user attempted to connect to WebSocket.')

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            logger.info(f'User {self.user_id} disconnected from group {self.room_group_name}')

    async def notify(self, event):
        message = event['message']
        logger.info(f'Notification sent to user {self.user_id}: {message}')
        await self.send(text_data=json.dumps({
            'message': message
        }))

    @database_sync_to_async
    def fetch_notifications(self):
        notifications = Notification.objects.filter(recipient=self.scope["user"], read=False)
        return list(notifications.values())
