from django.urls import path
from .views import send_notification, list_notifications, user_dashboard, delete_post

urlpatterns = [
    path('send_notification/', send_notification, name='send_notification'),
    path('list_notifications/', list_notifications, name='list_notifications'),
    path('dashboard/', user_dashboard, name='user_dashboard'),
    path('delete_post/<int:post_id>/', delete_post, name='delete_post'),  # Nova rota para exclusão de posts
]

