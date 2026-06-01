"""
Local development settings for evaluation_service.
"""
from .base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = ['*']

# Use Django's development server
INSTALLED_APPS += ['django.contrib.staticfiles']  # noqa: F405

# Show SQL queries in development
LOGGING['loggers']['django.db.backends'] = {  # noqa: F405
    'handlers': ['console'],
    'level': 'DEBUG',
    'propagate': False,
}

# Allow all CORS origins in development
CORS_ALLOW_ALL_ORIGINS = True

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
