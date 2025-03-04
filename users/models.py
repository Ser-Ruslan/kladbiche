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

    def create_modification_request(self, cemetery_object, request_type, description):
        return ObjectModificationRequest.objects.create(
            object=cemetery_object,
            request_type=request_type,
            description=description,
            updated_by=self
        )

    def search_objects(self, criteria):
        # Реализация поиска объектов по критериям
        return CemeteryObject.objects.filter(**criteria)