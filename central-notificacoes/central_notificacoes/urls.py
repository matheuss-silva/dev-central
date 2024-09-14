from django.contrib import admin
from django.urls import path, include
from notificacoes.views import auto_login
from notificacoes import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from notificacoes.views import get_posts

urlpatterns = [
    path('admin/', admin.site.urls),
    path('notificacoes/', include('notificacoes.urls')),
    path('auto-login/', auto_login, name='auto_login'),
    path('home/', views.home, name='home'),
    path('api/posts/', get_posts, name='get_posts'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

