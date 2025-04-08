import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def list_users():
    print("Список всех пользователей в системе:")
    print("-" * 70)
    print(f"{'ID':<5} {'Email':<30} {'Имя':<15} {'Активен':<10} {'Суперпользователь':<15} {'Персонал':<10} {'Роль':<10}")
    print("-" * 70)
    
    for user in User.objects.all():
        print(f"{user.id:<5} {user.email:<30} {user.username:<15} {'Да' if user.is_active else 'Нет':<10} {'Да' if user.is_superuser else 'Нет':<15} {'Да' if user.is_staff else 'Нет':<10} {user.role:<10}")

if __name__ == "__main__":
    list_users()