"""
WSGI config for flag_service.

Exposes the WSGI callable as a module-level variable named ``application``.
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flag_service.settings.local")

application = get_wsgi_application()
