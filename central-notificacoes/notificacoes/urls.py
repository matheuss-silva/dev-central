from django.urls import path
from .views import notifications, send_notification, list_notifications

urlpatterns = [
    path('', notifications, name='notifications'),
    path('send_notification/', send_notification, name='send_notification'),

]
