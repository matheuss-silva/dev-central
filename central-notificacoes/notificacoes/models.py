from django.db import models
from django.contrib.auth import get_user_model

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


class Event(models.Model):
    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('paused', 'Pausado'),
        ('finished', 'Finalizado'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField()
    logo = models.ImageField(upload_to='events/logos/', null=True, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.notify_status_change()

    def auto_update_status(self):
        from django.utils.timezone import now
        old_status = self.status

        if now() > self.end_date:
            self.status = 'finished'
        elif self.start_date <= now() <= self.end_date:
            self.status = 'active'
        else:
            self.status = 'paused'

        if old_status != self.status:
            self.save()

    def notify_status_change(self):
        """Notifica os clientes sobre a mudança de status do evento."""
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'event_status',
            {
                'type': 'send_event_status',  # Deve corresponder ao tipo esperado no consumidor
                'name': self.name,
                'description': self.description,
                'start_date': self.start_date.strftime('%d/%m/%Y %H:%M'),
                'end_date': self.end_date.strftime('%d/%m/%Y %H:%M'),
                'status': self.get_status_display(),
            }
        )

