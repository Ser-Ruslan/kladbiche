import os
import sys
import json
import datetime

# Добавляем проект Django в sys.path
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_path)

# Устанавливаем переменную окружения для настроек Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cemetery_map.settings")  # Замените на имя вашего проекта

# Инициализация Django
import django
django.setup()

# Теперь можно импортировать модели и другие компоненты Django
from django.db import connection, transaction

def convert_datetime(dt_str):
    if dt_str is None:
        return None
    try:
        dt = datetime.datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S.%f')
    except:
        return dt_str

def update_tables_from_json(json_dir='.'):
    # Получаем список JSON файлов
    json_files = [f for f in os.listdir(json_dir) if f.endswith('.json')]
    
    with transaction.atomic():
        with connection.cursor() as cursor:
            for json_file in json_files:
                try:
                    file_path = os.path.join(json_dir, json_file)
                    table_name = os.path.splitext(json_file)[0]
                    
                    # Чтение данных из JSON
                    with open(file_path, 'r', encoding='utf-8') as file:
                        data = json.load(file)
                    
                    if not data:
                        print(f"Файл {json_file} пуст. Пропускаем.")
                        continue
                    
                    print(f"Обработка файла {json_file} для таблицы {table_name}...")
                    
                    # Получаем колонки
                    columns = list(data[0].keys())
                    
                    # Очистка таблицы
                    cursor.execute(f"DELETE FROM {table_name}")
                    
                    # Формирование SQL
                    placeholders = ', '.join(['%s' for _ in columns])
                    column_names = ', '.join(columns)
                    
                    sql = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"
                    
                    # Вставка данных
                    for record in data:
                        values = []
                        for column in columns:
                            value = record[column]
                            if isinstance(value, str) and ('date' in column.lower() or 
                                                        'time' in column.lower() or 
                                                        column.lower() in ['created_at', 'updated_at', 'last_login', 'date_joined', 'last_activity', 'applied']):
                                value = convert_datetime(value)
                            values.append(value)
                        
                        cursor.execute(sql, values)
                    
                    print(f"Успешно обновлено {len(data)} записей в таблице {table_name}")
                    
                except Exception as e:
                    print(f"Ошибка при обработке файла {json_file}: {str(e)}")
                    raise  # Прерываем выполнение и откатываем транзакцию
    
    print("Обновление базы данных завершено успешно.")

if __name__ == "__main__":
    # Если указан путь к директории в аргументах, используем его
    if len(sys.argv) > 1:
        json_dir = sys.argv[1]
        update_tables_from_json(json_dir)
    else:
        update_tables_from_json()