from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """
    Расширение стандартной модели пользователя Django
    """
    ROLE_CHOICES = (
        ('user', 'Пользователь'),
        ('admin', 'Администратор'),
    )
    
    email = models.EmailField(_('email адрес'), unique=True)
    role = models.CharField(_('роль'), max_length=10, choices=ROLE_CHOICES, default='user')
    is_active = models.BooleanField(_('активирован'), default=False)
    date_joined = models.DateTimeField(_('дата регистрации'), default=timezone.now)
    last_activity = models.DateTimeField(_('последняя активность'), auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = _('пользователь')
        verbose_name_plural = _('пользователи')
    
    def __str__(self):
        return self.email
    
    @property
    def is_admin(self):
        """
        Проверка, является ли пользователь администратором
        """
        return self.role == 'admin'


class ActivationToken(models.Model):
    """
    Токен для подтверждения регистрации
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activation_tokens')
    token = models.CharField(_('токен'), max_length=255, unique=True)
    created_at = models.DateTimeField(_('дата создания'), auto_now_add=True)
    expires_at = models.DateTimeField(_('дата истечения'))
    
    class Meta:
        verbose_name = _('токен активации')
        verbose_name_plural = _('токены активации')
    
    def __str__(self):
        return f"Токен для {self.user.email}"
    
    def is_valid(self):
        """
        Проверка действительности токена
        """
        return timezone.now() < self.expires_at
