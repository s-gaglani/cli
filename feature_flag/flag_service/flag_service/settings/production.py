"""
Production settings for flag_service.

Usage:
    DJANGO_SETTINGS_MODULE=flag_service.settings.production

IMPORTANT: Never commit secrets to source control. All sensitive values must
be provided via environment variables or a secrets manager.
"""
from decouple import Csv, config

from .base import *  # noqa: F401, F403

# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------
DEBUG = False

ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv())

# HTTPS / HSTS
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000          # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Cookies
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# Clickjacking
X_FRAME_OPTIONS = "DENY"

# Content type sniffing
SECURE_CONTENT_TYPE_NOSNIFF = True

# XSS filter
SECURE_BROWSER_XSS_FILTER = True

# ---------------------------------------------------------------------------
# Database — production should use connection pooling (e.g. PgBouncer)
# ---------------------------------------------------------------------------
DATABASES["default"]["CONN_MAX_AGE"] = 600  # noqa: F405

# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------
STATIC_ROOT = "/app/staticfiles"

# ---------------------------------------------------------------------------
# CORS — tighten to real origins in production
# ---------------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = False

# ---------------------------------------------------------------------------
# Email backend
# ---------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST", default="")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")

# ---------------------------------------------------------------------------
# Cache (optional — uncomment to enable Redis caching)
# ---------------------------------------------------------------------------
# CACHES = {
#     "default": {
#         "BACKEND": "django.core.cache.backends.redis.RedisCache",
#         "LOCATION": config("REDIS_URL", default="redis://localhost:6379/0"),
#     }
# }
