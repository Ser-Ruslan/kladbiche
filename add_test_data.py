import os
import django
import random
from datetime import datetime, timedelta

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

# Импортируем после настройки Django
from users.models import User
from graves.models import Grave, PersonalNote, FavoriteGrave, EditProposal
from notifications.models import Notification

def create_test_graves(admin_user):
    """Создает тестовые захоронения"""
    # Подготовим координаты нескольких полигонов для могил (примерно в районе указанного кладбища)
    base_lat, base_lon = 52.033635, 113.501049
    graves_data = [
        {
            'full_name': 'Иванов Иван Иванович',
            'birth_date': datetime(1950, 5, 15).date(),
            'death_date': datetime(2020, 10, 25).date(),
            'description': 'Любящий отец и дедушка. Ветеран труда.',
            'polygon_coordinates': generate_polygon_coordinates(base_lat, base_lon, 0.0001, 0.0002),
            'created_by': admin_user
        },
        {
            'full_name': 'Петрова Мария Сергеевна',
            'birth_date': datetime(1945, 3, 8).date(),
            'death_date': datetime(2018, 7, 12).date(),
            'description': 'Заслуженный учитель Российской Федерации. Посвятила жизнь образованию.',
            'polygon_coordinates': generate_polygon_coordinates(base_lat + 0.0003, base_lon + 0.0004, 0.0001, 0.0002),
            'created_by': admin_user
        },
        {
            'full_name': 'Сидоров Петр Алексеевич',
            'birth_date': datetime(1963, 11, 23).date(),
            'death_date': datetime(2019, 4, 30).date(),
            'description': 'Талантливый инженер. Автор нескольких изобретений.',
            'polygon_coordinates': generate_polygon_coordinates(base_lat - 0.0003, base_lon - 0.0005, 0.0001, 0.0002),
            'created_by': admin_user
        },
        {
            'full_name': 'Кузнецова Анна Ивановна',
            'birth_date': datetime(1973, 8, 17).date(),
            'death_date': datetime(2021, 1, 5).date(),
            'description': 'Врач высшей категории. Спасла множество жизней.',
            'polygon_coordinates': generate_polygon_coordinates(base_lat + 0.0005, base_lon - 0.0003, 0.0001, 0.0002),
            'created_by': admin_user
        },
        {
            'full_name': 'Смирнов Алексей Петрович',
            'birth_date': datetime(1935, 12, 1).date(),
            'death_date': datetime(2017, 9, 20).date(),
            'description': 'Ветеран Великой Отечественной войны. Награжден множеством медалей.',
            'polygon_coordinates': generate_polygon_coordinates(base_lat - 0.0006, base_lon + 0.0006, 0.0001, 0.0002),
            'created_by': admin_user
        }
    ]
    
    created_graves = []
    for grave_data in graves_data:
        grave, created = Grave.objects.get_or_create(
            full_name=grave_data['full_name'],
            defaults=grave_data
        )
        if created:
            print(f"Создано захоронение: {grave.full_name}")
        else:
            print(f"Захоронение уже существует: {grave.full_name}")
        created_graves.append(grave)
    
    return created_graves

def generate_polygon_coordinates(base_lat, base_lon, width, height):
    """Генерирует координаты полигона для захоронения"""
    # Создаем прямоугольный полигон с небольшим случайным отклонением
    points = [
        [base_lon - width/2 + random.uniform(-0.00001, 0.00001), base_lat - height/2 + random.uniform(-0.00001, 0.00001)],
        [base_lon + width/2 + random.uniform(-0.00001, 0.00001), base_lat - height/2 + random.uniform(-0.00001, 0.00001)],
        [base_lon + width/2 + random.uniform(-0.00001, 0.00001), base_lat + height/2 + random.uniform(-0.00001, 0.00001)],
        [base_lon - width/2 + random.uniform(-0.00001, 0.00001), base_lat + height/2 + random.uniform(-0.00001, 0.00001)]
    ]
    return str(points)

def create_test_user():
    """Создает тестового пользователя"""
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'testuser@example.com',
            'is_active': True
        }
    )
    
    if created:
        user.set_password('testpassword')
        user.save()
        print(f"Создан тестовый пользователь: {user.username} (пароль: testpassword)")
    else:
        print(f"Тестовый пользователь уже существует: {user.username}")
    
    return user

def create_test_personal_notes(user, graves):
    """Создает тестовые личные заметки"""
    for grave in graves[:3]:  # Создаем заметки только для первых трех захоронений
        note, created = PersonalNote.objects.get_or_create(
            user=user,
            grave=grave,
            defaults={
                'text': f'Моя личная заметка для захоронения {grave.full_name}. Посетил(а) {random.randint(1, 10)} раз.'
            }
        )
        
        if created:
            print(f"Создана личная заметка для захоронения {grave.full_name}")
        else:
            print(f"Личная заметка для захоронения {grave.full_name} уже существует")

def create_test_favorites(user, graves):
    """Добавляет тестовые захоронения в избранное"""
    for grave in random.sample(graves, min(3, len(graves))):  # Добавляем в избранное до 3 случайных захоронений
        favorite, created = FavoriteGrave.objects.get_or_create(
            user=user,
            grave=grave
        )
        
        if created:
            print(f"Захоронение {grave.full_name} добавлено в избранное")
        else:
            print(f"Захоронение {grave.full_name} уже в избранном")

def create_test_edit_proposals(user, graves):
    """Создает тестовые предложения по редактированию"""
    # Добавляем предложение для одного случайного захоронения
    grave = random.choice(graves)
    proposal, created = EditProposal.objects.get_or_create(
        user=user,
        grave=grave,
        defaults={
            'proposed_description': f'{grave.description} Дополнительная информация: занимался благотворительностью, помогал малоимущим семьям.',
            'status': 'pending'
        }
    )
    
    if created:
        print(f"Создано предложение по редактированию для захоронения {grave.full_name}")
        # Создаем уведомление для администратора
        admin = User.objects.filter(is_superuser=True).first()
        if admin:
            Notification.objects.create(
                user=admin,
                notification_type='edit_proposal',
                message=f'Новое предложение по редактированию для захоронения {grave.full_name}',
                related_id=proposal.id
            )
            print(f"Создано уведомление для администратора о новом предложении")
    else:
        print(f"Предложение по редактированию для захоронения {grave.full_name} уже существует")

def main():
    """Основная функция для создания тестовых данных"""
    print("Начинаем создание тестовых данных...")
    
    # Получаем администратора
    admin = User.objects.filter(is_superuser=True).first()
    if not admin:
        print("Ошибка: не найден суперпользователь. Сначала создайте суперпользователя.")
        return
    
    # Создаем тестовые захоронения
    graves = create_test_graves(admin)
    
    # Создаем тестового пользователя
    user = create_test_user()
    
    # Создаем тестовые личные заметки
    create_test_personal_notes(user, graves)
    
    # Добавляем тестовые захоронения в избранное
    create_test_favorites(user, graves)
    
    # Создаем тестовые предложения по редактированию
    create_test_edit_proposals(user, graves)
    
    print("Тестовые данные успешно созданы!")

if __name__ == "__main__":
    main()