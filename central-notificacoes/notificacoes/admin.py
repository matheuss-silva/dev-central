from django.contrib import admin
from .models import Notification, Post
from .views import send_notification_to_group, send_post_to_users


class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'message', 'created_at']
    search_fields = ['title', 'message']
    readonly_fields = ['created_at']
    exclude = ['recipient']

    def has_module_permission(self, request):
        """
        Permite acesso ao painel de notificações apenas para usuários staff.
        """
        return request.user.is_staff

    def save_model(self, request, obj, form, change):
        """
        Salva a notificação no banco de dados e envia via WebSocket para todos os usuários conectados.
        """
        obj.save()
        send_notification_to_group(obj.message)


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at')
    search_fields = ('title', 'subtitle')
    readonly_fields = ('created_at',)

    def get_queryset(self, request):
        """
        Filtra os posts exibidos no admin:
        - Usuários staff podem visualizar todos os posts.
        - Usuários não staff veem apenas seus próprios posts.
        """
        queryset = super().get_queryset(request)
        if request.user.is_staff:
            return queryset
        return queryset.filter(author=request.user)

    def has_change_permission(self, request, obj=None):
        """
        Permite que usuários não staff editem apenas seus próprios posts.
        """
        if obj and not request.user.is_staff and obj.author != request.user:
            return False
        return super().has_change_permission(request, obj=obj)

    def has_delete_permission(self, request, obj=None):
        """
        Permite que usuários não staff excluam apenas seus próprios posts.
        """
        if obj and not request.user.is_staff and obj.author != request.user:
            return False
        return super().has_delete_permission(request, obj=obj)

    def save_model(self, request, obj, form, change):
        """
        Define o autor do post como o usuário autenticado ao salvar um novo post.
        """
        if not obj.pk:  # Se for um novo objeto
            obj.author = request.user
        super().save_model(request, obj, form, change)


# Registra os modelos no Django Admin
admin.site.register(Notification, NotificationAdmin)
admin.site.register(Post, PostAdmin)
