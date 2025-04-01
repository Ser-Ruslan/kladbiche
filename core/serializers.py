from rest_framework import serializers
from .models import Cemetery, Burial, UserNote, FavoriteBurial, BurialRequest
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'is_staff')


class CemeterySerializer(serializers.ModelSerializer):
    class Meta:
        model = Cemetery
        fields = '__all__'


class BurialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Burial
        fields = '__all__'


class UserNoteSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())

    class Meta:
        model = UserNote
        fields = '__all__'
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class FavoriteBurialSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())
    burial_details = BurialSerializer(source='burial', read_only=True)

    class Meta:
        model = FavoriteBurial
        fields = ('id', 'user', 'burial', 'burial_details', 'created_at')
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class BurialRequestSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())

    class Meta:
        model = BurialRequest
        fields = ('id', 'user', 'cemetery', 'full_name', 'birth_date', 
                  'death_date', 'latitude', 'longitude', 'description', 
                  'status', 'rejection_reason', 'created_at', 'updated_at')
        read_only_fields = ('status', 'rejection_reason', 'approved_burial')
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class BurialRequestAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = BurialRequest
        fields = '__all__'
        read_only_fields = ('user', 'cemetery', 'full_name', 'birth_date', 
                           'death_date', 'latitude', 'longitude', 'description', 
                           'created_at', 'updated_at')


class BurialListSerializer(serializers.ModelSerializer):
    is_favorite = serializers.SerializerMethodField()
    
    class Meta:
        model = Burial
        fields = ('id', 'full_name', 'birth_date', 'death_date', 
                  'latitude', 'longitude', 'is_favorite')
    
    def get_is_favorite(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return FavoriteBurial.objects.filter(user=user, burial=obj).exists()


class BurialDetailSerializer(BurialSerializer):
    is_favorite = serializers.SerializerMethodField()
    user_note = serializers.SerializerMethodField()
    
    class Meta:
        model = Burial
        fields = '__all__'
    
    def get_is_favorite(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return FavoriteBurial.objects.filter(user=user, burial=obj).exists()
    
    def get_user_note(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return None
        try:
            note = UserNote.objects.get(user=user, burial=obj)
            return UserNoteSerializer(note).data
        except UserNote.DoesNotExist:
            return None
