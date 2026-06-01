"""
Local development settings for project_service.
Uses DEBUG=True, allows all hosts, enables browsable API.
"""
from .base import *  # noqa: F401, F403

# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------
DEBUG = True
ALLOWED_HOSTS = ['*']

# ---------------------------------------------------------------------------
# DRF — keep browsable API in local
# ---------------------------------------------------------------------------
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [  # noqa: F405
    'rest_framework.renderers.JSONRenderer',
    'rest_framework.renderers.BrowsableAPIRenderer',
]

# ---------------------------------------------------------------------------
# Django Extensions (optional — install separately if needed)
# ---------------------------------------------------------------------------
# INSTALLED_APPS += ['django_extensions']

# ---------------------------------------------------------------------------
# Email backend — print to console
# ---------------------------------------------------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
