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

