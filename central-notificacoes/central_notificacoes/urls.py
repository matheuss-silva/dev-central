from django.contrib import admin
from django.urls import path, include
from notificacoes.views import login_view, register_user, home
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', login_view, name='login'),
    path('admin/', admin.site.urls),
    path('notificacoes/', include('notificacoes.urls')),
    path('register/', register_user, name='register'),
    path('home/', home, name='home'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
