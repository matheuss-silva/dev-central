from django.contrib import admin
from .models import Notification, Post
from .views import send_notification_to_group, send_post_to_users

class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'message', 'created_at']  # Exibe apenas os campos necessários na lista
    search_fields = ['title', 'message']  # Campos para pesquisa
    readonly_fields = ['created_at']  # Campos somente leitura no formulário
    exclude = ['recipient']  # Oculta o campo `recipient` do formulário de criação/edição

    def save_model(self, request, obj, form, change):
        """
        Salva a notificação no banco de dados e envia via WebSocket para todos os usuários conectados.
        """
        obj.save()  # Salva a notificação no banco de dados
        send_notification_to_group(obj.message)  # Envia a notificação para o grupo global

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at')
    search_fields = ('title', 'subtitle')
    readonly_fields = ('created_at',)

    def save_model(self, request, obj, form, change):
        """
        Salva o post e envia via WebSocket para todos os usuários conectados.
        """
        obj.author = request.user  # Define o autor como o usuário autenticado
        obj.save()  # Salva o post no banco de dados
        send_post_to_users(obj)  # Envia o post via WebSocket para todos os usuários conectados

# Registra os modelos no Django Admin
admin.site.register(Notification, NotificationAdmin)
admin.site.register(Post, PostAdmin)
