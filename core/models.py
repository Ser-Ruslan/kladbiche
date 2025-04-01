from django.db import models
from django.contrib.auth.models import User


class Cemetery(models.Model):
    """Модель кладбища"""
    name = models.CharField(max_length=255, verbose_name="Название")
    latitude = models.FloatField(verbose_name="Широта")
    longitude = models.FloatField(verbose_name="Долгота")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Кладбище"
        verbose_name_plural = "Кладбища"


class Burial(models.Model):
    """Модель захоронения"""
    cemetery = models.ForeignKey(Cemetery, on_delete=models.CASCADE, related_name="burials", verbose_name="Кладбище")
    full_name = models.CharField(max_length=255, verbose_name="ФИО")
    birth_date = models.DateField(blank=True, null=True, verbose_name="Дата рождения")
    death_date = models.DateField(blank=True, null=True, verbose_name="Дата смерти")
    latitude = models.FloatField(verbose_name="Широта")
    longitude = models.FloatField(verbose_name="Долгота")
    admin_description = models.TextField(blank=True, null=True, verbose_name="Описание администратора")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    def __str__(self):
        return self.full_name
    
    class Meta:
        verbose_name = "Захоронение"
        verbose_name_plural = "Захоронения"
        indexes = [
            models.Index(fields=['full_name']),
            models.Index(fields=['birth_date']),
            models.Index(fields=['death_date']),
        ]


class UserNote(models.Model):
    """Модель пользовательских заметок"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notes", verbose_name="Пользователь")
    burial = models.ForeignKey(Burial, on_delete=models.CASCADE, related_name="user_notes", verbose_name="Захоронение")
    text = models.TextField(verbose_name="Текст")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    def __str__(self):
        return f"Заметка {self.user.username} о {self.burial.full_name}"
    
    class Meta:
        verbose_name = "Заметка пользователя"
        verbose_name_plural = "Заметки пользователей"
        unique_together = ['user', 'burial']


class FavoriteBurial(models.Model):
    """Модель избранных захоронений"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites", verbose_name="Пользователь")
    burial = models.ForeignKey(Burial, on_delete=models.CASCADE, related_name="favorited_by", verbose_name="Захоронение")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    def __str__(self):
        return f"{self.user.username} - {self.burial.full_name}"
    
    class Meta:
        verbose_name = "Избранное захоронение"
        verbose_name_plural = "Избранные захоронения"
        unique_together = ['user', 'burial']


class BurialRequest(models.Model):
    """Модель запросов на добавление захоронений"""
    STATUS_CHOICES = (
        ('pending', 'На рассмотрении'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="burial_requests", verbose_name="Пользователь")
    cemetery = models.ForeignKey(Cemetery, on_delete=models.CASCADE, related_name="burial_requests", verbose_name="Кладбище")
    full_name = models.CharField(max_length=255, verbose_name="ФИО")
    birth_date = models.DateField(blank=True, null=True, verbose_name="Дата рождения")
    death_date = models.DateField(blank=True, null=True, verbose_name="Дата смерти")
    latitude = models.FloatField(verbose_name="Широта")
    longitude = models.FloatField(verbose_name="Долгота")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    rejection_reason = models.TextField(blank=True, null=True, verbose_name="Причина отклонения")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    approved_burial = models.ForeignKey(Burial, blank=True, null=True, on_delete=models.SET_NULL, related_name="request", verbose_name="Одобренное захоронение")
    
    def __str__(self):
        return f"Запрос от {self.user.username}: {self.full_name} ({self.status})"
    
    class Meta:
        verbose_name = "Запрос на добавление"
        verbose_name_plural = "Запросы на добавление"
