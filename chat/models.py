
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    links = models.URLField(null=True, blank=True)  # For personal or social media links
    status = models.CharField(max_length=20, default='active')  # Example statuses: active, inactive, etc.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.username


class Message(models.Model):
    sender = models.ForeignKey(CustomUser, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(CustomUser, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)  # Tracks when the message was read
    status = models.CharField(max_length=20, default='sent')  # Example statuses: sent, delivered, read


    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Message from {self.sender} to {self.receiver} at {self.timestamp}'
    


