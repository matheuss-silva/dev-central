import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Notification
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Adiciona todos os WebSockets ao grupo global
        self.room_group_name = 'notifications_group'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Remove o WebSocket do grupo global
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def notify(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({'message': message}))

    @database_sync_to_async
    def fetch_notifications(self):
        notifications = Notification.objects.filter(recipient=self.scope["user"], read=False)
        return list(notifications.values())

class PostConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'posts_group'

        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def post_message(self, event):
        post = event['post']

        # Envia o post para o WebSocket
        await self.send(text_data=json.dumps({
            'action': 'add',
            'post': post
        }))

    async def delete_post_message(self, event):
        post_id = event['post_id']
        logger.info(f"Mensagem de exclusão enviada para o WebSocket: Post ID {post_id}")
        await self.send(text_data=json.dumps({
            'action': 'delete',
            'post_id': post_id
        }))
