from django.contrib import admin
from .models import Notification, Post
from .views import send_notification_to_users, send_post_to_users

class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'message', 'created_at']
    search_fields = ['title', 'message']
    readonly_fields = ['created_at']
    
    def save_model(self, request, obj, form, change):
        obj.save()
        send_notification_to_users(obj)  # Envia notificação para o grupo WebSocket

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title', 'subtitle')
    readonly_fields = ('created_at',)

    def save_model(self, request, obj, form, change):
        obj.save()
        send_post_to_users(obj)  # Envia post para o grupo WebSocket

# Registra os modelos no Django Admin
admin.site.register(Notification, NotificationAdmin)
admin.site.register(Post, PostAdmin)
