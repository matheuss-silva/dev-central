import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Notification
from django.contrib.auth.models import AnonymousUser

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Verifique se o usuário está autenticado
        if self.scope["user"].is_authenticated:
            # Captura o user_id do usuário autenticado
            self.user_id = str(self.scope["user"].id)
            self.room_group_name = f'notifications_{self.user_id}'

            # Inscreve no grupo
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            # Aceita a conexão WebSocket
            await self.accept()
        else:
            # Se o usuário não está autenticado, rejeite a conexão
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
        # Envie a mensagem para o WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

    @database_sync_to_async
    def fetch_notifications(self):
        notifications = Notification.objects.filter(recipient=self.user, read=False)
        return list(notifications.values())
