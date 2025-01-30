from django.db import models
from django.contrib.auth import get_user_model
from django.utils.timezone import now, make_aware, is_aware
from datetime import datetime

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

    def __str__(self):
        return self.title


class EventSchedule(models.Model):
    event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='schedules')
    date = models.DateField()  # Data específica do evento
    start_time = models.TimeField()  # Hora de início
    end_time = models.TimeField()  # Hora de término

    class Meta:
        unique_together = ('event', 'date')  # Garante que um evento tenha apenas um registro por dia

    def __str__(self):
        return f"{self.event.name} - {self.date} ({self.start_time} - {self.end_time})"


class Event(models.Model):
    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('paused', 'Pausado'),
        ('finished', 'Finalizado'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField()
    logo = models.ImageField(upload_to='events/logos/', null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='paused')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Ao salvar um novo evento, ele inicia como 'Pausado' e depois muda automaticamente no horário certo.
        """
        is_new = self.pk is None

        if is_new:
            self.status = 'paused'

        super().save(*args, **kwargs)

        if not is_new:
            self.auto_update_status()

        # 🔹 Notifica WebSocket automaticamente após qualquer alteração
        self.notify_status_change()

    def auto_update_status(self):
        """
        Atualiza automaticamente o status do evento com base nos horários definidos na programação.
        """
        if not self.pk:
            return

        current_datetime = now()
        today_schedule = self.schedules.filter(date=current_datetime.date()).first()

        if today_schedule:
            start_datetime = today_schedule.start_time
            end_datetime = today_schedule.end_time

            if start_datetime <= current_datetime.time() <= end_datetime:
                new_status = 'active'
            elif current_datetime.time() > end_datetime:
                new_status = 'finished'
            else:
                new_status = 'paused'
        else:
            new_status = 'paused'

        if self.status != new_status:
            self.status = new_status
            self.save(update_fields=['status'])  # 🔹 Agora sempre salva corretamente
            self.notify_status_change()

    def notify_status_change(self):
        """Notifica os clientes via WebSocket sobre a mudança de status do evento."""
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'event_status',
            {
                'type': 'send_event_status',
                'id': self.id,
                'name': self.name,
                'description': self.description,
                'status': self.get_status_display(),
                'logo_url': self.logo.url if self.logo else None,
            }
        )
