from django.contrib import admin
from .models import CustomUser, Message

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'status', 'created_at', 'updated_at']
    search_fields = ['username', 'email']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'status', 'created_at', 'read_at']
    search_fields = ['sender__username', 'receiver__username', 'content']
