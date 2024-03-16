import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Notification

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_anonymous:
            # Rejeita a conexão se o usuário não estiver autenticado
            await self.close()
        else:
            self.user = self.scope["user"]
            self.group_name = f'notifications_{self.user.id}'

            # Entrar no grupo de notificações do usuário
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )

            await self.accept()

    async def disconnect(self, close_code):
        # Sair do grupo quando o WebSocket se desconectar
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Lidar com as mensagens recebidas pelo WebSocket
        text_data_json = json.loads(text_data)
        action = text_data_json.get('action')

        if action == 'fetch_notifications':
            # Enviar as notificações pendentes para o usuário
            notifications = await self.fetch_notifications()
            await self.send(text_data=json.dumps({
                'notifications': notifications
            }))

    async def send_notification(self, event):
        # Event handler que será chamado quando uma notificação for enviada para o grupo
        message = event['message']

        # Enviar a mensagem para o WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

    @database_sync_to_async
    def fetch_notifications(self):
        # Buscar notificações não lidas para o usuário
        notifications = Notification.objects.filter(recipient=self.user, read=False)
        return list(notifications.values())
