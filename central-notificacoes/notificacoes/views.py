# notificacoes/views.py
from django.shortcuts import render
from django.http import HttpResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.views.decorators.csrf import csrf_exempt

def notifications(request):
    return render(request, 'notificacoes/notifications.html', {'user_id': request.user.id})

@csrf_exempt
def send_notification(request):
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        message = request.POST.get('message')
        if not user_id or not message:
            return HttpResponse("Invalid data", status=400)
        
        channel_layer = get_channel_layer()
        group_name = f'notifications_{user_id}'

        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'notify',
                'message': message,
            }
        )

        return HttpResponse("Notificação enviada", status=200)
    else:
        return HttpResponse("Erro ao enviar notificação", status=405)
