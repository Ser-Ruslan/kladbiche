from django.contrib import admin
from .models import Cemetery, Burial, UserNote, FavoriteBurial, BurialRequest


@admin.register(Cemetery)
class CemeteryAdmin(admin.ModelAdmin):
    list_display = ('name', 'latitude', 'longitude')
    search_fields = ('name',)


@admin.register(Burial)
class BurialAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'birth_date', 'death_date', 'cemetery')
    list_filter = ('cemetery',)
    search_fields = ('full_name',)
    date_hierarchy = 'death_date'


@admin.register(UserNote)
class UserNoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'burial', 'created_at', 'updated_at')
    list_filter = ('user',)
    search_fields = ('user__username', 'burial__full_name', 'text')


@admin.register(FavoriteBurial)
class FavoriteBurialAdmin(admin.ModelAdmin):
    list_display = ('user', 'burial', 'created_at')
    list_filter = ('user',)
    search_fields = ('user__username', 'burial__full_name')


@admin.register(BurialRequest)
class BurialRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'status', 'created_at')
    list_filter = ('status', 'cemetery')
    search_fields = ('user__username', 'full_name')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
