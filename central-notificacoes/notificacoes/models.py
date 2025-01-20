from django.db import models
from django.contrib.auth import get_user_model 

class Notification(models.Model):
    recipient = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        null=True,  # Permite valores nulos no banco de dados
        blank=True  # Permite deixar o campo em branco no Django Admin
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.recipient:
            return f'Notification for {self.recipient.username}: {self.title}'
        return f'Notification (Global): {self.title}'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'read': self.read,
        }

User = get_user_model()

class Post(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255)
    image = models.ImageField(upload_to='posts/', null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
