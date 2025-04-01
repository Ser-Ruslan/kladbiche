"""
WSGI config for cemetery_map project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cemetery_map.settings')

application = get_wsgi_application()
