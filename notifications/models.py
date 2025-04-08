from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class Notification(models.Model):
    """
    Модель уведомлений для пользователей
    """
    NOTIFICATION_TYPES = (
        ('system', 'Системное уведомление'),
        ('edit_proposal', 'Предложение редактирования'),
        ('proposal_status', 'Статус предложения'),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('пользователь')
    )
    notification_type = models.CharField(
        _('тип уведомления'),
        max_length=20,
        choices=NOTIFICATION_TYPES,
        default='system'
    )
    message = models.TextField(_('сообщение'))
    is_read = models.BooleanField(_('прочитано'), default=False)
    created_at = models.DateTimeField(_('дата создания'), auto_now_add=True)
    related_id = models.IntegerField(_('ID связанной сущности'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('уведомление')
        verbose_name_plural = _('уведомления')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Уведомление для {self.user.username}: {self.message[:30]}..."
