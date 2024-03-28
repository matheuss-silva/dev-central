import json
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect

def auto_login(request):
    user = authenticate(username='admin', password='12341234')
    if user is not None:
        login(request, user)
        return HttpResponseRedirect('/notificacoes/')
    else:
        return HttpResponse("Falha no login", status=401) 


def notifications(request):
    # Verifique se o usuário está autenticado
    if request.user.is_authenticated:
        # Passe o ID do usuário autenticado para o contexto
        return render(request, 'notificacoes/notifications.html', {'user_id_json': json.dumps(request.user.id)})
    else:
        # Se o usuário não estiver autenticado, você pode decidir o que fazer
        # Talvez redirecionar para a página de login ou passar 'null' como fallback
        return render(request, 'notificacoes/notifications.html', {'user_id_json': 'null'})


@csrf_exempt
def send_notification(request):
    if request.method != "POST":
        return JsonResponse({'error': 'Método inválido'}, status=405)

    user_id = request.POST.get('user_id')
    message = request.POST.get('message')
    if not user_id or not message:
        return JsonResponse({'error': 'Dados inválidos'}, status=400)
    
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
        return JsonResponse({'success': 'Notificacao enviada'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
