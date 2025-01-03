import json
import logging
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Notification, Post
from django.contrib.admin.views.decorators import staff_member_required


logger = logging.getLogger(__name__)

User = get_user_model()

def login_view(request):
    """
    Exibe a tela de login e autentica o usuário.
    """
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            logger.info(f'User {user.username} logged in successfully.')
            return redirect('/home/')  # Redireciona para a página home
        else:
            logger.error('Failed login attempt.')
            return render(request, 'notificacoes/login.html', {'error': 'Credenciais inválidas. Tente novamente.'})
    
    return render(request, 'notificacoes/login.html')

def register_user(request):
    """
    Exibe a tela de registro e cria um novo usuário.
    """
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            return render(request, 'notificacoes/register.html', {'error': 'As senhas não coincidem.'})

        try:
            user = User.objects.create_user(username=username, password=password)
            user.save()
            logger.info(f'User {user.username} registered successfully.')
            return redirect('/')  # Redireciona para a tela de login
        except Exception as e:
            logger.error(f'Error during user registration: {e}')
            return render(request, 'notificacoes/register.html', {'error': 'Erro ao criar a conta. Tente novamente.'})
    
    return render(request, 'notificacoes/register.html')


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

@staff_member_required
@csrf_exempt
def send_notification(request):
    if request.method == "POST":
        message = request.POST.get('message')
        title = request.POST.get('title', 'No Title')

        if not message:
            return JsonResponse({'error': 'Dados inválidos'}, status=400)

        try:
            # Cria a notificação
            notification = Notification.objects.create(
                recipient=None,  # Nenhum destinatário específico
                title=title,
                message=message,
                read=False
            )

            # Envia a notificação para todos os usuários conectados
            send_notification_to_group(notification.message)
            
            return JsonResponse({'success': 'Notificação enviada para todos os usuários conectados'}, status=200)
        
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


def send_notification_to_group(message):
    """
    Envia uma notificação para todos os usuários conectados ao grupo global de notificações.
    """
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'notifications_group',  # Nome do grupo global
            {
                'type': 'notify',  # Tipo de mensagem
                'message': message,  # Conteúdo da mensagem
            }
        )
        logger.info(f'Notificação enviada para o grupo global de notificações.')
    except Exception as e:
        logger.error(f'Erro ao enviar notificação para o grupo global: {str(e)}')

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

@login_required
def user_dashboard(request):
    """
    Exibe os posts do usuário autenticado e permite criar novos posts.
    """
    error = None

    if request.method == 'POST':
        title = request.POST.get('title')
        subtitle = request.POST.get('subtitle')
        image = request.FILES.get('image')

        if title and subtitle:
            try:
                # Criação do post
                post = Post.objects.create(
                    title=title,
                    subtitle=subtitle,
                    image=image,
                    author=request.user
                )

                # Enviar o post via WebSocket
                channel_layer = get_channel_layer()
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

            except Exception as e:
                error = f"Ocorreu um erro ao criar o post: {e}"
        else:
            error = "Por favor, preencha todos os campos obrigatórios."

    posts = Post.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'notificacoes/dashboard.html', {'posts': posts, 'error': error})



@login_required
def delete_post(request, post_id):
    """
    Exclui um post pertencente ao usuário autenticado.
    """
    post = get_object_or_404(Post, id=post_id, author=request.user)
    post.delete()

    # Enviar uma mensagem de exclusão via WebSocket (se necessário)
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'posts_group',
        {
            'type': 'delete_post_message',
            'post_id': post_id
        }
    )

    return redirect('user_dashboard')
