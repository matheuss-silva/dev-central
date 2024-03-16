from django.db import models
from django.conf import settings

class Notification(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.recipient.username} - {self.title}"

