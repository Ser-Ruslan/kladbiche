from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class Grave(models.Model):
    """
    Модель захоронения
    """
    # Координаты полигона в формате GeoJSON
    polygon_coordinates = models.TextField(_('координаты полигона'))
    
    full_name = models.CharField(_('ФИО погребенного'), max_length=255)
    birth_date = models.DateField(_('дата рождения'), null=True, blank=True)
    death_date = models.DateField(_('дата смерти'), null=True, blank=True)
    description = models.TextField(_('описание'), blank=True)
    
    created_at = models.DateTimeField(_('дата добавления'), auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_graves',
        verbose_name=_('добавлено администратором')
    )
    
    class Meta:
        verbose_name = _('захоронение')
        verbose_name_plural = _('захоронения')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.full_name


class PersonalNote(models.Model):
    """
    Личные заметки пользователей к захоронениям
    """
    grave = models.ForeignKey(
        Grave,
        on_delete=models.CASCADE,
        related_name='personal_notes',
        verbose_name=_('захоронение')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='personal_notes',
        verbose_name=_('пользователь')
    )
    text = models.TextField(_('текст заметки'))
    created_at = models.DateTimeField(_('дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('дата обновления'), auto_now=True)
    
    class Meta:
        verbose_name = _('личная заметка')
        verbose_name_plural = _('личные заметки')
        ordering = ['-updated_at']
        unique_together = ['grave', 'user']
    
    def __str__(self):
        return f"Заметка {self.user.username} к {self.grave.full_name}"


class FavoriteGrave(models.Model):
    """
    Избранные захоронения пользователей
    """
    grave = models.ForeignKey(
        Grave,
        on_delete=models.CASCADE,
        related_name='favorite_marks',
        verbose_name=_('захоронение')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorite_graves',
        verbose_name=_('пользователь')
    )
    created_at = models.DateTimeField(_('дата добавления'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('избранное захоронение')
        verbose_name_plural = _('избранные захоронения')
        ordering = ['-created_at']
        unique_together = ['grave', 'user']
    
    def __str__(self):
        return f"{self.grave.full_name} в избранном у {self.user.username}"


class EditProposal(models.Model):
    """
    Предложения редактирования от пользователей
    """
    STATUS_CHOICES = (
        ('pending', 'На модерации'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
    )
    
    grave = models.ForeignKey(
        Grave,
        on_delete=models.CASCADE,
        related_name='edit_proposals',
        verbose_name=_('захоронение')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='edit_proposals',
        verbose_name=_('пользователь')
    )
    proposed_description = models.TextField(_('предлагаемое описание'))
    status = models.CharField(
        _('статус'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    rejection_reason = models.TextField(_('причина отклонения'), blank=True)
    created_at = models.DateTimeField(_('дата предложения'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('предложение редактирования')
        verbose_name_plural = _('предложения редактирования')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Предложение редактирования для {self.grave.full_name} от {self.user.username}"
