from django.apps import apps

# Ленивая загрузка моделей
def get_user_model():
    return apps.get_model('users', 'User')

def get_cemetery_model():
    return apps.get_model('cemeteries', 'Cemetery')

def get_burial_model():
    return apps.get_model('burials', 'Burial')

# Список экспорта ленивых функций
__all__ = ['get_user_model', 'get_cemetery_model', 'get_burial_model']