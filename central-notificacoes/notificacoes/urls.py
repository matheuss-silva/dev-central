from django.urls import path
from .views import notifications
from .views import send_notification
from . import views


urlpatterns = [
    path('', notifications, name='notifications'),
    path('send_notification/', views.send_notification, name='send_notification'),
]