from rest_framework import serializers
from django.contrib.auth import get_user_model
from graves.models import Grave, PersonalNote, FavoriteGrave, EditProposal
from notifications.models import Notification

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для пользователей
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'date_joined')
        read_only_fields = ('id', 'date_joined')


class GraveSerializer(serializers.ModelSerializer):
    """
    Сериализатор для захоронений
    """
    is_favorite = serializers.SerializerMethodField()
    
    class Meta:
        model = Grave
        fields = ('id', 'full_name', 'birth_date', 'death_date', 'description', 
                  'polygon_coordinates', 'created_at', 'is_favorite')
    
    def get_is_favorite(self, obj):
        """
        Проверяет, добавлено ли захоронение в избранное текущим пользователем
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return FavoriteGrave.objects.filter(grave=obj, user=request.user).exists()
        return False


class PersonalNoteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для личных заметок
    """
    class Meta:
        model = PersonalNote
        fields = ('id', 'grave', 'text', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def create(self, validated_data):
        """
        Создает или обновляет заметку для текущего пользователя
        """
        user = self.context['request'].user
        grave = validated_data.get('grave')
        
        note, created = PersonalNote.objects.update_or_create(
            user=user,
            grave=grave,
            defaults={'text': validated_data.get('text')}
        )
        
        return note


class FavoriteGraveSerializer(serializers.ModelSerializer):
    """
    Сериализатор для избранных захоронений
    """
    grave_detail = GraveSerializer(source='grave', read_only=True)
    
    class Meta:
        model = FavoriteGrave
        fields = ('id', 'grave', 'grave_detail', 'created_at')
        read_only_fields = ('id', 'created_at')
    
    def create(self, validated_data):
        """
        Создает запись об избранном захоронении для текущего пользователя
        """
        user = self.context['request'].user
        grave = validated_data.get('grave')
        
        favorite, created = FavoriteGrave.objects.get_or_create(
            user=user,
            grave=grave
        )
        
        return favorite


class EditProposalSerializer(serializers.ModelSerializer):
    """
    Сериализатор для предложений редактирования
    """
    user_username = serializers.ReadOnlyField(source='user.username')
    grave_name = serializers.ReadOnlyField(source='grave.full_name')
    
    class Meta:
        model = EditProposal
        fields = ('id', 'grave', 'grave_name', 'user', 'user_username', 'proposed_description', 
                  'status', 'rejection_reason', 'created_at')
        read_only_fields = ('id', 'user', 'status', 'rejection_reason', 'created_at')
    
    def create(self, validated_data):
        """
        Создает предложение редактирования для текущего пользователя
        """
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class NotificationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для уведомлений
    """
    class Meta:
        model = Notification
        fields = ('id', 'notification_type', 'message', 'is_read', 'created_at', 'related_id')
        read_only_fields = ('id', 'notification_type', 'message', 'created_at', 'related_id')
