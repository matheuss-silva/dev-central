from django.contrib import admin
from django.urls import path, include
from notificacoes.views import auto_login
from notificacoes import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('notificacoes/', include('notificacoes.urls')),
    path('auto-login/', auto_login, name='auto_login'),
    path('home/', views.home, name='home'),
    
]

