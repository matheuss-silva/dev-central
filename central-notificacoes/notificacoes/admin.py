from django.contrib import admin
from .models import Notification
from .views import send_notification_to_user  # Importa o método criado no views.py

class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'title', 'message', 'created_at']
    search_fields = ['recipient__username', 'title', 'message']

    def save_model(self, request, obj, form, change):
        """
        Este método é chamado sempre que uma notificação é salva no Django Admin.
        Ele garante que a notificação seja enviada via WebSocket após ser salva.
        """
        obj.save()  # Salva a notificação no banco de dados
        send_notification_to_user(obj.recipient.id, obj.message)  # Envia a notificação via WebSocket

admin.site.register(Notification, NotificationAdmin)
