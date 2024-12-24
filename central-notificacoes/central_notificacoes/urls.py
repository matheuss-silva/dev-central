from django.contrib import admin
from django.urls import path, include
from notificacoes import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('notificacoes/', include('notificacoes.urls')),
    path('api/notifications/', views.notifications, name='notifications'),
    path('api/posts/', views.get_posts, name='get_posts'),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
