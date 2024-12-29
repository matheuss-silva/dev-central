from django.urls import path
from .views import send_notification, list_notifications

urlpatterns = [
    path('send_notification/', send_notification, name='send_notification'),
    path('list_notifications/', list_notifications, name='list_notifications'),
]

