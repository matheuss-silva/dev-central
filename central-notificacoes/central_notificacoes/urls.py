from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # URL do painel de administração
    path('notificacoes/', include('notificacoes.urls')),  # Inclua as rotas do app `notificacoes`
]
