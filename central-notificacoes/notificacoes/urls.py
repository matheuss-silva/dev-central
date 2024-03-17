from django.urls import path
from . import views
from .views import notifications

urlpatterns = [
    path('notifications/', views.notifications, name='show_notifications'),
]