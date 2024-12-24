from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Notification, Post
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

# API para listar todos os posts
@api_view(['GET'])
def get_posts(request):
    posts = Post.objects.all().order_by('-created_at')
    posts_list = [
        {
            'title': post.title,
            'subtitle': post.subtitle,
            'image_url': post.image.url if post.image else '',
            'author': post.author.username,
        } for post in posts
    ]
    return Response(posts_list)

# API para listar todas as notificações
@api_view(['GET'])
def notifications(request):
    notifications = Notification.objects.all().order_by('-created_at')
    notifications_list = [
        {
            'title': notification.title,
            'message': notification.message,
        } for notification in notifications
    ]
    return Response(notifications_list)

# Função para enviar posts a todos os usuários conectados
def send_post_to_users(post):
    # Obter o canal para enviar as mensagens do WebSocket
    channel_layer = get_channel_layer()
    
    # Enviar mensagem para o grupo de WebSocket "posts_group"
    async_to_sync(channel_layer.group_send)(
        'posts_group',
        {
            'type': 'post_message',
            'post': {
                'title': post.title,
                'subtitle': post.subtitle,
                'image_url': post.image.url if post.image else '',
                'author': post.author.username,
            }
        }
    )

# Função para enviar notificações a todos os usuários conectados
def send_notification_to_users(notification):
    # Obter o canal para enviar as mensagens do WebSocket
    channel_layer = get_channel_layer()
    
    # Enviar mensagem para o grupo de WebSocket "notifications_group"
    async_to_sync(channel_layer.group_send)(
        'notifications_group',
        {
            'type': 'notify',
            'notification': {
                'title': notification.title,
                'message': notification.message,
            }
        }
    )
