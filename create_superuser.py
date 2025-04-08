import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth import get_user_model
from users.models import User

User = get_user_model()

def create_superuser():
    try:
        # Проверяем, существует ли уже пользователь с таким email
        if User.objects.filter(email='admin777@example.com').exists():
            print("Пользователь с email admin777@example.com уже существует! Обновляем данные.")
            user = User.objects.get(email='admin777@example.com')
            user.set_password('AdmiN777')
            user.username = 'admin777'
            user.is_superuser = True
            user.is_staff = True
            user.role = 'admin'
            user.is_active = True  # Важно: активируем пользователя
            user.save()
            print("Данные пользователя admin777@example.com успешно обновлены.")
        else:
            # Создаем нового суперпользователя
            user = User.objects.create_user(
                username='admin777',
                email='admin777@example.com',
                password='AdmiN777'
            )
            # Настраиваем права и активируем
            user.is_superuser = True
            user.is_staff = True
            user.role = 'admin'
            user.is_active = True  # Активируем пользователя
            user.save()
            print("Суперпользователь admin777@example.com успешно создан!")
        
        return True
    except Exception as e:
        print(f"Ошибка при создании суперпользователя: {e}")
        return False

if __name__ == "__main__":
    create_superuser()