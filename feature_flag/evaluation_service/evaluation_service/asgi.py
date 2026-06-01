"""
ASGI config for evaluation_service project.
"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'evaluation_service.settings.local')

application = get_asgi_application()
