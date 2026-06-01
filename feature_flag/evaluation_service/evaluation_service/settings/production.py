"""
Production settings for evaluation_service.
"""
from .base import *  # noqa: F401, F403
from decouple import config

DEBUG = False

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Only use HTTPS in production (set SECURE_SSL_REDIRECT=True if behind HTTPS)
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=False, cast=bool)
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=True, cast=bool)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=True, cast=bool)

# Database connection pooling
DATABASES['default']['CONN_MAX_AGE'] = 600  # noqa: F405

# Static files with WhiteNoise (optional, for serving static files in production)
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# Logging - more verbose in production for monitoring
LOGGING['handlers']['console']['formatter'] = 'verbose'  # noqa: F405
LOGGING['root']['level'] = 'WARNING'  # noqa: F405
LOGGING['loggers']['apps.evaluation']['level'] = 'INFO'  # noqa: F405

# CORS - must explicitly set origins in production
CORS_ALLOW_ALL_ORIGINS = False
