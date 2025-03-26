# myproject/context_processors.py

from django.conf import settings

def yandex_maps_api_key(request):
    return {'yandex_maps_api_key': settings.YANDEX_MAPS_API_KEY}
