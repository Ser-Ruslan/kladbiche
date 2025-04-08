import uuid
from datetime import timedelta
from django.utils import timezone

def generate_activation_token():
    """
    Генерирует уникальный токен для активации аккаунта
    """
    return str(uuid.uuid4())


def create_token_expires_time():
    """
    Создает время истечения токена (3 дня от текущего времени)
    """
    return timezone.now() + timedelta(days=3)
