"""
ASGI config for cemetery_map project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cemetery_map.settings')

application = get_asgi_application()
