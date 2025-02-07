from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
    re_path(r'ws/posts/(?P<user_id>\d+)/$', consumers.PostConsumer.as_asgi()),
    re_path(r'ws/event/$', consumers.EventConsumer.as_asgi()),
]
