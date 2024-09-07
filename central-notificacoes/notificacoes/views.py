import json
import logging
from django.contrib.auth import authenticate, login, get_user_model
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.decorators import login_required
from .models import Notification
from .models import Post


logger = logging.getLogger(__name__)

User = get_user_model()  # Aqui o modelo de usuário é recuperado

def auto_login(request):
    user = authenticate(username='admin', password='12341234')
    if user is not None:
        login(request, user)
        logger.info(f'User {user.username} logged in successfully.')
        return HttpResponseRedirect('/notificacoes/')
    else:
        logger.error('Failed login attempt for user admin.')
        return HttpResponse("Falha no login", status=401)

def notifications(request):
    if request.user.is_authenticated:
        user_notifications = Notification.objects.filter(recipient=request.user, read=False)
        notifications_json = json.dumps([notification.to_dict() for notification in user_notifications])
        logger.info(f'Notifications fetched for user {request.user.id}')
        return render(request, 'notificacoes/notifications.html', {
            'user_id_json': json.dumps(request.user.id),
            'notifications_json': notifications_json,
        })
    else:
        logger.warning('Unauthenticated user attempted to access notifications.')
        return HttpResponseRedirect('/auto-login/')

@login_required
def home(request):
    """
    View para a tela home que passa o user_id e os posts para o template.
    """
    user_id_json = json.dumps(request.user.id)
    
    # Buscar todas as postagens
    posts = Post.objects.all().order_by('-created_at')  # Ordenar da mais recente para a mais antiga
    
    return render(request, 'notificacoes/home.html', {
        'user_id_json': user_id_json,
        'posts': posts  # Enviar as postagens para o template
    })

@csrf_exempt
def send_notification(request):
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        message = request.POST.get('message')
        title = request.POST.get('title', 'No Title')

        if not user_id or not message:
            return JsonResponse({'error': 'Dados inválidos'}, status=400)

        try:
            user = User.objects.get(id=user_id)
            notification = Notification.objects.create(recipient=user, title=title, message=message, read=False)

            # Enviar notificação via WebSocket
            send_notification_to_user(user_id, notification.message)
            
            return JsonResponse({'success': 'Notificação enviada e armazenada'}, status=200)
        
        except User.DoesNotExist:
            return JsonResponse({'error': 'Usuário não encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Método inválido'}, status=405)


@csrf_exempt
def mark_notification_as_read(request):
    if request.method == 'POST':
        notification_id = request.POST.get('notification_id')
        try:
            notification = Notification.objects.get(id=notification_id, recipient=request.user)
            notification.read = True
            notification.save()
            logger.info(f'Notification {notification_id} marcada como lida para user {request.user.id}.')
            return JsonResponse({'success': 'Notificação marcada como lida'})
        except Notification.DoesNotExist:
            logger.error(f'mark_notification_as_read: Notificação {notification_id} não encontrada para o usuário {request.user.id}.')
            return JsonResponse({'error': 'Notificação não encontrada'}, status=404)
    else:
        logger.warning('mark_notification_as_read: Método inválido acessado.')
        return JsonResponse({'error': 'Método inválido'}, status=405)


def list_notifications(request):
    if not request.user.is_authenticated:
        logger.warning('list_notifications: Usuário não autenticado tentou acessar.')
        return JsonResponse({'error': 'Usuário não autenticado'}, status=401)

    notifications = Notification.objects.filter(recipient=request.user, read=False)
    logger.info(f'Listando notificações para usuário {request.user.id}')
    return render(request, 'notificacoes/list_notifications.html', {'notifications': notifications})


def send_notification_to_user(user_id, message):
    """
    Método para enviar notificação para um usuário específico via WebSocket
    """
    try:
        channel_layer = get_channel_layer()
        group_name = f'notifications_{user_id}'
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'notify',
                'message': message,
            }
        )
        logger.info(f'Notificação enviada para user_id {user_id} via WebSocket.')
    except Exception as e:
        logger.error(f'Erro ao enviar notificação via WebSocket para user_id {user_id}: {str(e)}')

def send_post_to_users(post):
    """
    Envia uma nova postagem para todos os usuários conectados ao WebSocket.
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'posts_group',  # Nome do grupo do WebSocket
        {
            'type': 'post_message',  # Tipo de evento que será capturado pelo WebSocket
            'post': {
                'title': post.title,
                'subtitle': post.subtitle,
                'image_url': post.image.url if post.image else '',
                'author': post.author.username,
            }
        }
    )
