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
        ('waiting', 'Aguardando Início'),
        ('active', 'Ativo'),
        ('closed', 'Encerrado (dia)'),
        ('finished', 'Finalizado'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField()
    logo = models.ImageField(upload_to='events/logos/', null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='waiting')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Salva um evento garantindo que alterações manuais e automáticas funcionem corretamente.
        """
        is_new = self.pk is None  # Verifica se é um evento novo
        status_anterior = None

        if not is_new:
            # Obtém o status antes da alteração
            status_anterior = Event.objects.get(pk=self.pk).status  

        super().save(*args, **kwargs)  # Salva o evento

        if is_new:
            # Se for novo, define "Aguardando Início"
            self.status = 'waiting'
            self.save(update_fields=['status'])
            self.notify_status_change()

        elif status_anterior and status_anterior != self.status:
            # Se foi alterado manualmente no Admin, dispara notificação WebSocket
            self.notify_status_change()

        # **Não alterar se o status for "Ativo" manualmente**
        if self.status != 'active':
            self.auto_update_status()

    def auto_update_status(self):
        """
        Atualiza automaticamente o status do evento baseado no horário programado.
        Se o evento estiver como "Ativo", não reverte a atualização manual.
        """
        if not self.pk or self.status == 'active':  # Não altera status ativo manualmente
            return

        current_datetime = now()
        today_schedule = self.schedules.filter(date=current_datetime.date()).first()

        if today_schedule:
            start_time = today_schedule.start_time
            end_time = today_schedule.end_time

            if start_time <= current_datetime.time() < end_time:
                new_status = 'active'
            elif current_datetime.time() >= end_time:
                new_status = 'closed'
            else:
                new_status = 'waiting'
        else:
            new_status = 'finished'  # Se não houver programação, finaliza o evento

        if self.status != new_status:
            self.status = new_status
            self.save(update_fields=['status'])
            self.notify_status_change()

    def notify_status_change(self):
        """Notifica os clientes WebSocket sobre a mudança de status do evento."""
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
                'status': self.status,  # Envia diretamente o status correto
                'logo_url': self.logo.url if self.logo else None,
            }
        )