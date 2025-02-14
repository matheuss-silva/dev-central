from django.db import models
from django.utils.timezone import now
from django.contrib.auth import get_user_model
import threading
import time

User = get_user_model()


class Notification(models.Model):
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.recipient:
            return f'Notification for {self.recipient.username}: {self.title}'
        return f'Notification (Global): {self.title}'

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'read': self.read,
        }


class Post(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255)
    image = models.ImageField(upload_to='posts/', null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    event = models.ForeignKey('Event', on_delete=models.CASCADE, null=True, blank=True) 

    def __str__(self):
        return self.title


class EventSchedule(models.Model):
    event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='schedules')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField() 
    class Meta:
        unique_together = ('event', 'date') 

    def __str__(self):
        return f"{self.event.name} - {self.date} ({self.start_time} - {self.end_time})"


class Event(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'Aguardando Início'),
        ('active', 'Ativo'),
        ('closed', 'Encerrado (dia)'),
        ('finished', 'Finalizado'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField()
    logo = models.ImageField(upload_to='events/logos/', null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='waiting')
    manual_override = models.BooleanField(default=False) 

    def save(self, *args, **kwargs):
        """ Garante que eventos novos comecem como 'Aguardando Início' e não sobrescreve status manual. """
        is_new = self.pk is None
        if is_new:
            self.status = 'waiting' 

        super().save(*args, **kwargs)
        if not is_new and not self.manual_override:
            self.auto_update_status()

    def auto_update_status(self):
        """Verifica e atualiza automaticamente o status do evento com base no horário programado."""
        if self.manual_override:
            return 
        
        current_datetime = now()
        today_schedule = self.schedules.filter(date=current_datetime.date()).first()
        future_schedules = self.schedules.filter(date__gt=current_datetime.date()).exists()
        new_status = self.status

        if today_schedule:
            start_time = today_schedule.start_time
            end_time = today_schedule.end_time
            if start_time <= current_datetime.time() < end_time:
                new_status = 'active'
            elif current_datetime.time() >= end_time:
                new_status = 'closed' if future_schedules else 'finished'
        else:
            new_status = 'finished' if not future_schedules else 'waiting'

        if self.status != new_status:
            self.status = new_status
            self.save(update_fields=['status'])
            self.notify_status_change() 

    def notify_status_change(self):
        """Envia uma notificação via WebSocket quando o status do evento é alterado."""
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        status_mapping = {
            'waiting': 'Aguardando Início',
            'active': 'Ativo',
            'closed': 'Encerrado (dia)',
            'finished': 'Finalizado'
        }

        channel_layer = get_channel_layer()

        try:
            async_to_sync(channel_layer.group_send)(
                'event_status',
                {
                    'type': 'send_event_status',
                    'id': self.id,
                    'name': self.name,
                    'description': self.description,
                    'status': status_mapping.get(self.status, self.status),
                    'logo_url': self.logo.url if self.logo else None,
                }
            )
            print(f"✅ Evento atualizado e notificado: {self.name} - {status_mapping.get(self.status, self.status)}")
        except Exception as e:
            print(f"⚠️ Erro ao enviar atualização WebSocket: {e}")



def schedule_event_status_updates():
    """Cria um agendador para verificar periodicamente o status dos eventos e atualizar automaticamente."""
    while True:
        try:
            time.sleep(60)
            events = Event.objects.all()
            for event in events:
                event.auto_update_status()
        except Exception as e:
            print(f"⚠️ Erro ao atualizar status do evento: {e}")
            time.sleep(10)

if "event_scheduler" not in globals():
    event_scheduler = threading.Thread(target=schedule_event_status_updates, daemon=True)
    event_scheduler.start()
