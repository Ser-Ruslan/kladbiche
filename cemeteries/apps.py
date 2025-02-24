from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import sessionmaker
from cemeteries.models import Cemetery, db  # Импорт db и Cemetery из models.py
import os
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 1. Создаем приложение и настраиваем конфигурацию
app = Flask(__name__)
app.secret_key = os.urandom(24)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Отключаем уведомления об изменениях для производительности
db.init_app(app)  # Инициализируем SQLAlchemy с приложением
migrate = Migrate(app, db)  # Настраиваем миграции


# 2. Определяем маршрут для главной страницы
@app.route('/')
def index():
    try:
        # Получаем список всех кладбищ из базы данных
        with app.app_context():  # Убедимся, что есть контекст приложения
            cemeteries = Cemetery.query.all()
        return render_template('templates/index.html', cemeteries=cemeteries)
    except Exception as e:
        # Логика обработки ошибок с использованием логирования
        logger.error(f"Ошибка при получении списка кладбищ: {str(e)}")
        return "Произошла внутренняя ошибка сервера", 500

# 3. Функция для инициализации базы данных
def init_db():
    with app.app_context():
        # Создаем таблицы, если их еще нет
        db.create_all()
        # Проверяем, есть ли записи, и добавляем тестовые данные, если их нет


if __name__ == '__main__':
    # Инициализируем базу данных перед запуском приложения
    init_db()
    # Запускаем приложение в режиме отладки
    app.run(debug=True)