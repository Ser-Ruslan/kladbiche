from django.contrib import admin
from .models import Grave, PersonalNote, FavoriteGrave, EditProposal

@admin.register(Grave)
class GraveAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'birth_date', 'death_date', 'created_at', 'created_by')
    list_filter = ('created_at',)
    search_fields = ('full_name',)
    date_hierarchy = 'created_at'


@admin.register(PersonalNote)
class PersonalNoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'grave', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'grave__full_name', 'text')


@admin.register(FavoriteGrave)
class FavoriteGraveAdmin(admin.ModelAdmin):
    list_display = ('user', 'grave', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__email', 'grave__full_name')


@admin.register(EditProposal)
class EditProposalAdmin(admin.ModelAdmin):
    list_display = ('user', 'grave', 'status', 'created_at', 'get_current_description', 'get_proposed_description')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'user__email', 'grave__full_name', 'proposed_description')
    date_hierarchy = 'created_at'
    readonly_fields = ('user', 'grave', 'proposed_description', 'created_at', 'current_description_display')
    fieldsets = (
        ('Информация о предложении', {
            'fields': ('user', 'grave', 'created_at', 'status')
        }),
        ('Содержание', {
            'fields': ('current_description_display', 'proposed_description')
        }),
        ('Модерация', {
            'fields': ('rejection_reason',),
            'description': 'Если вы отклоняете предложение, укажите причину отклонения. Оставьте пустым при одобрении.'
        }),
    )
    
    def get_current_description(self, obj):
        """Получить текущее описание захоронения (для списка)"""
        if obj.grave.description:
            return obj.grave.description[:50] + '...' if len(obj.grave.description) > 50 else obj.grave.description
        return 'Описание отсутствует'
    get_current_description.short_description = 'Текущее описание'
    
    def get_proposed_description(self, obj):
        """Получить предлагаемое описание (для списка)"""
        return obj.proposed_description[:50] + '...' if len(obj.proposed_description) > 50 else obj.proposed_description
    get_proposed_description.short_description = 'Предлагаемое описание'
    
    def current_description_display(self, obj):
        """Отобразить текущее описание захоронения (для формы)"""
        return obj.grave.description if obj.grave.description else 'Описание отсутствует'
    current_description_display.short_description = 'Текущее описание захоронения'
    
    def save_model(self, request, obj, form, change):
        """При сохранении модели отправляем уведомление и обновляем описание если статус изменен"""
        old_status = None
        if change:
            try:
                old_obj = EditProposal.objects.get(pk=obj.pk)
                old_status = old_obj.status
            except EditProposal.DoesNotExist:
                pass
        
        super().save_model(request, obj, form, change)
        
        # Если статус изменен на "одобрено", обновляем описание захоронения
        if change and old_status != obj.status:
            if obj.status == 'approved':
                # Обновляем описание захоронения
                grave = obj.grave
                grave.description = obj.proposed_description
                grave.save()
                
                # Отправляем уведомление пользователю
                from notifications.utils import notify_user_about_proposal_status
                notify_user_about_proposal_status(obj, True)
            
            elif obj.status == 'rejected':
                # Отправляем уведомление об отклонении
                from notifications.utils import notify_user_about_proposal_status
                notify_user_about_proposal_status(obj, False)
