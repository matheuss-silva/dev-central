import json
import logging
import asyncio
import redis
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Notification, Event, EventSchedule
from asgiref.sync import async_to_sync
from django.utils.timezone import now


logger = logging.getLogger(__name__)

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Conecta o WebSocket ao grupo de notificações"""
        self.room_group_name = 'notifications_group'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        """Remove o WebSocket do grupo de notificações"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def notify(self, event):
        """Envia notificações para os usuários conectados"""
        message = event['message']
        await self.send(text_data=json.dumps({'message': message}))

    @database_sync_to_async
    def fetch_notifications(self):
        """Busca notificações não lidas para o usuário autenticado"""
        notifications = Notification.objects.filter(recipient=self.scope["user"], read=False)
        return list(notifications.values())


class EventConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Conecta o WebSocket ao grupo de status de eventos"""
        self.room_group_name = 'event_status'
        
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Enviar evento atual ao conectar
        await self.send_current_event()

    async def disconnect(self, close_code):
        """Remove o WebSocket do grupo de eventos corretamente"""
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def send_current_event(self):
        """Envia os detalhes do evento ativo para os clientes WebSocket"""
        event = await self.get_active_event()

        if event:
            await self.send_event_status(event)
        else:
            await self.send(text_data=json.dumps({'error': 'Nenhum evento disponível no momento.'}))

    async def send_event_status(self, event):
        """Envia a atualização do evento para o WebSocket"""
        if isinstance(event, dict):
            event = await self.get_event_by_id(event.get("id"))

        if event is None:
            await self.send(text_data=json.dumps({'error': 'Nenhum evento válido encontrado para exibir.'}))
            return

        schedule = await self.get_today_schedule(event.id)
        start_date = schedule["start_date"] if schedule else "Não disponível"
        end_date = schedule["end_date"] if schedule else "Não disponível"

        status_mapping = {
            'waiting': 'Aguardando Início',
            'active': 'Ativo',
            'closed': 'Encerrado (dia)',
            'finished': 'Finalizado'
        }

        event_data = {
            'id': event.id,
            'name': event.name,
            'description': event.description,
            'start_date': start_date,
            'end_date': end_date,
            'status': status_mapping.get(event.status, event.status),
            'logo_url': event.logo.url if event.logo else None,
        }

        logger.info(f"📡 Enviando atualização de evento via WebSocket: {event_data}")
        await self.send(text_data=json.dumps(event_data))

    async def receive(self, text_data):
        """Recebe comandos WebSocket, como 'refresh' para atualizar o evento"""
        data = json.loads(text_data)
        action = data.get("action")

        if action == "refresh":
            event = await self.get_active_event()
            if event:
                await self.send_event_status(event)

    @database_sync_to_async
    def get_active_event(self):
        """Busca o evento ativo e atualiza seu status antes de enviá-lo."""
        event = Event.objects.exclude(status='finished').first()
        if event:
            event.auto_update_status()
        return event

    @database_sync_to_async
    def get_event_by_id(self, event_id):
        """Busca um evento específico pelo ID"""
        return Event.objects.filter(id=event_id).first()

    @database_sync_to_async
    def get_today_schedule(self, event_id):
        """Busca o horário do evento para a data atual"""
        today = now().date()
        event = Event.objects.filter(id=event_id).first()
        if event:
            schedule = event.schedules.filter(date=today).first()
            if schedule:
                return {
                    "start_date": schedule.start_time.strftime('%H:%M'),
                    "end_date": schedule.end_time.strftime('%H:%M')
                }
        return None


class PostConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Conecta o WebSocket ao grupo de postagens"""
        self.room_group_name = 'posts_group'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        """Remove o WebSocket do grupo de postagens"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def post_message(self, event):
        """Envia uma nova postagem para os clientes WebSocket"""
        post = event['post']

        await self.send(text_data=json.dumps({
            'action': 'add',
            'post': post
        }))

    async def delete_post_message(self, event):
        """Envia um evento de exclusão para os clientes WebSocket"""
        post_id = event['post_id']
        logger.info(f"Mensagem de exclusão enviada para o WebSocket: Post ID {post_id}")

        await self.send(text_data=json.dumps({
            'action': 'delete',
            'post_id': post_id
        }))
