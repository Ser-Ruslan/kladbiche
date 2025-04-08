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
    list_display = ('user', 'grave', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'user__email', 'grave__full_name', 'proposed_description')
    date_hierarchy = 'created_at'
