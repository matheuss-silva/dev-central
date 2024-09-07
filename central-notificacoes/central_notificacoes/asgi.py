import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'central_notificacoes.settings')

# Inicialize o Django antes de qualquer outra coisa
django.setup()

# Agora você pode importar o roteamento sem problemas
import notificacoes.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            notificacoes.routing.websocket_urlpatterns
        )
    ),
})
