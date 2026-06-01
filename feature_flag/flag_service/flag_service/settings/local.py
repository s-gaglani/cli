"""
Local / development settings for flag_service.

Usage:
    DJANGO_SETTINGS_MODULE=flag_service.settings.local
"""
from .base import *  # noqa: F401, F403

# ---------------------------------------------------------------------------
# Debug
# ---------------------------------------------------------------------------
DEBUG = True

# ---------------------------------------------------------------------------
# Development-only apps
# ---------------------------------------------------------------------------
INSTALLED_APPS += []  # noqa: F405  # add dev tools here if needed

# ---------------------------------------------------------------------------
# Allow all hosts locally
# ---------------------------------------------------------------------------
ALLOWED_HOSTS = ["*"]

# ---------------------------------------------------------------------------
# Email backend (console for development)
# ---------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ---------------------------------------------------------------------------
# Django debug toolbar (optional — install separately)
# ---------------------------------------------------------------------------
# INSTALLED_APPS += ["debug_toolbar"]
# MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
# INTERNAL_IPS = ["127.0.0.1"]
