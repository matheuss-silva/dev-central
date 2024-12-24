import json
from channels.generic.websocket import AsyncWebsocketConsumer

class PostConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'posts_group'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        print(f"Conectado ao grupo {self.room_group_name}")  # Adiciona print
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"Desconectado do grupo {self.room_group_name}")  # Adiciona print

    async def post_message(self, event):
        post = event['post']
        print(f"Enviando post: {post}")  # Adiciona print
        await self.send(text_data=json.dumps({
            'post': post
        }))

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'notifications_group'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        print(f"Conectado ao grupo {self.room_group_name}")  # Adiciona print
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"Desconectado do grupo {self.room_group_name}")  # Adiciona print

    async def notify(self, event):
        notification = event['notification']
        print(f"Enviando notificação: {notification}")  # Adiciona print
        await self.send(text_data=json.dumps({
            'notification': notification
        }))
