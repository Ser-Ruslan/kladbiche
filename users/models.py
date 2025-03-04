
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    USER_ROLES = (
        ('ADMIN', 'Administrator'),
        ('MODERATOR', 'Moderator'),
        ('USER', 'User'),
        ('GUEST', 'Guest')
    )
    
    role = models.CharField(max_length=20, choices=USER_ROLES, default='USER')
    created_at = models.DateTimeField(auto_now_add=True)

    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',  # Добавляем уникальный related_name
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_set',  # Добавляем уникальный related_name
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

