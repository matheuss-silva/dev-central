import json
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Notification

def auto_login(request):
    user = authenticate(username='admin', password='12341234')
    if user is not None:
        login(request, user)
        return HttpResponseRedirect('/notificacoes/')
    else:
        return HttpResponse("Falha no login", status=401)

def notifications(request):
    if request.user.is_authenticated:
        return render(request, 'notificacoes/notifications.html', {'user_id_json': json.dumps(request.user.id)})
    else:
        return HttpResponseRedirect('/auto-login/')  # Redireciona para auto-login se não estiver autenticado

@csrf_exempt
def send_notification(request):
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        message = request.POST.get('message')
        title = request.POST.get('title', 'No Title')

        if not user_id or not message:
            return JsonResponse({'error': 'Dados inválidos'}, status=400)

        try:
            user = get_user_model().objects.get(id=user_id)
            notification = Notification.objects.create(recipient=user, title=title, message=message, read=False)

            channel_layer = get_channel_layer()
            group_name = f'notifications_{user_id}'
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'notify',
                    'message': message,
                    'title': title,
                }
            )
            
            return JsonResponse({'success': 'Notificação enviada e armazenada'}, status=200)
        
        except get_user_model().DoesNotExist:
            return JsonResponse({'error': 'Usuário não encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Método inválido'}, status=405)

def list_notifications(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Usuário não autenticado'}, status=401)

    notifications = Notification.objects.filter(recipient=request.user, read=False)
    return render(request, 'notificacoes/list_notifications.html', {'notifications': notifications})

@csrf_exempt
def mark_notification_as_read(request):
    if request.method == 'POST':
        notification_id = request.POST.get('notification_id')
        try:
            notification = Notification.objects.get(id=notification_id, recipient=request.user)
            notification.read = True
            notification.save()
            return JsonResponse({'success': 'Notificação marcada como lida'})
        except Notification.DoesNotExist:
            return JsonResponse({'error': 'Notificação não encontrada'}, status=404)
