# Интерактивная карта кладбища

Это веб-приложение для интерактивной карты кладбища, позволяющее пользователям искать и получать информацию о захоронениях.

## Возможности

- Интерактивная карта с отображением захоронений в виде полигонов
- Система пользователей с ролями (гость, пользователь, администратор)
- Личные заметки и избранные захоронения для зарегистрированных пользователей
- Поиск по ФИО и датам
- Система предложений по редактированию и модерации
- API для возможной мобильной интеграции

## Учетные записи для тестирования

### Администратор
- Логин: admin777@example.com
- Пароль: AdmiN777

### Обычный пользователь
- Почта: testuser@example.com
- Пароль: testpassword

## Технологический стек

- **Бэкенд**: Python, Django, Django REST Framework
- **База данных**: PostgreSQL
- **Фронтенд**: HTML, CSS, JavaScript
- **Карты**: Яндекс.Карты API

## Структура проекта

- `cemetery_map/` - основная директория проекта с настройками
- `users/` - приложение для работы с пользователями
- `graves/` - приложение для работы с захоронениями
- `notifications/` - приложение для работы с уведомлениями
- `api/` - REST API интерфейс
- `static/` - статические файлы (CSS, JavaScript, изображения)
- `templates/` - HTML шаблоны

## Модели данных

- **User** - расширенная модель пользователя Django
- **Grave** - модель захоронения с координатами полигона и информацией о погребенном
- **PersonalNote** - личные заметки пользователей к захоронениям
- **FavoriteGrave** - избранные захоронения пользователей
- **EditProposal** - предложения пользователей по редактированию описаний захоронений
- **Notification** - уведомления для пользователей

## API Endpoints

- `/api/graves/` - управление захоронениями
- `/api/personal-notes/` - управление личными заметками
- `/api/favorites/` - управление избранными захоронениями
- `/api/edit-proposals/` - управление предложениями по редактированию
- `/api/notifications/` - получение и управление уведомлениями

## Разработка и запуск проекта

### Запуск сервера
```bash
python manage.py runserver 0.0.0.0:5000
```

### Добавление тестовых данных
```bash
python add_test_data.py
```

### Создание суперпользователя
```bash
python manage.py createsuperuser
```

## Лицензия

Этот проект лицензирован под MIT License - см. файл LICENSE для подробностей.