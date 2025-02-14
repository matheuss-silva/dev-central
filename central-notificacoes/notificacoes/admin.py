from django.contrib import admin
from .models import Notification, Post, Event, EventSchedule
from .views import send_notification_to_group, send_post_to_users


class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'message', 'created_at']
    search_fields = ['title', 'message']
    readonly_fields = ['created_at']
    exclude = ['recipient']

    def has_module_permission(self, request):
        """Restringe o acesso ao painel de notificações apenas para usuários staff."""
        return request.user.is_staff

    def save_model(self, request, obj, form, change):
        """Salva a notificação e a envia via WebSocket para todos os usuários conectados."""
        obj.save()
        send_notification_to_group(obj.message)


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at')
    search_fields = ('title', 'subtitle')
    readonly_fields = ('created_at',)

    def get_queryset(self, request):
        """Filtra posts no admin: staff vê todos, usuários comuns veem apenas seus próprios posts."""
        queryset = super().get_queryset(request)
        if request.user.is_staff:
            return queryset
        return queryset.filter(author=request.user)

    def has_change_permission(self, request, obj=None):
        """Permite que usuários comuns editem apenas seus próprios posts."""
        if obj and not request.user.is_staff and obj.author != request.user:
            return False
        return super().has_change_permission(request, obj=obj)

    def has_delete_permission(self, request, obj=None):
        """Permite que usuários comuns excluam apenas seus próprios posts."""
        if obj and not request.user.is_staff and obj.author != request.user:
            return False
        return super().has_delete_permission(request, obj=obj)

    def save_model(self, request, obj, form, change):
        """Define automaticamente o autor do post ao salvar um novo post."""
        if not obj.pk:
            obj.author = request.user
        super().save_model(request, obj, form, change)


class EventScheduleInline(admin.TabularInline):
    model = EventSchedule
    extra = 1  

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'status')
    list_filter = ('status',)
    search_fields = ('name',)
    inlines = [EventScheduleInline]

    def save_model(self, request, obj, form, change):
        """Garante que novos eventos sejam criados corretamente e impede alteração indevida do status."""
        if 'status' in form.changed_data:
            obj.manual_override = True  

        if not change: 
            obj.status = 'waiting'
        super().save_model(request, obj, form, change)
        obj.notify_status_change()


admin.site.register(Notification, NotificationAdmin)
admin.site.register(Post, PostAdmin)
