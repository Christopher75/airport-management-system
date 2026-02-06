"""
Django production settings for airport_system project.

Security-hardened settings for production deployment.
"""

from .base import *  # noqa: F401, F403
from decouple import config

# ============================================================
# Core Security Settings
# ============================================================

DEBUG = False

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="",
    cast=lambda v: [s.strip() for s in v.split(",") if s.strip()]
)

# Secret key must be set in environment
SECRET_KEY = config("SECRET_KEY")

# ============================================================
# Database Configuration
# ============================================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", default="airport_db"),
        "USER": config("DB_USER", default="postgres"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
        "CONN_MAX_AGE": 60,  # Persistent connections
        "OPTIONS": {
            "connect_timeout": 10,
        },
    }
}

# ============================================================
# Security Headers and HTTPS
# ============================================================

# Force HTTPS
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cookie Security
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"

# Prevent clickjacking
X_FRAME_OPTIONS = "DENY"

# Content type sniffing prevention
SECURE_CONTENT_TYPE_NOSNIFF = True

# XSS Filter
SECURE_BROWSER_XSS_FILTER = True

# Referrer Policy
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# ============================================================
# Session Security
# ============================================================

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
SESSION_CACHE_ALIAS = "default"
SESSION_COOKIE_AGE = 3600 * 24  # 24 hours
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = True

# ============================================================
# CORS Configuration
# ============================================================

CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default="",
    cast=lambda v: [s.strip() for s in v.split(",") if s.strip()]
)
CORS_ALLOW_CREDENTIALS = True

# ============================================================
# Cache Configuration (Redis)
# ============================================================

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": config("REDIS_URL"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 5,
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 50,
            },
        },
        "KEY_PREFIX": "naia_prod",
        "TIMEOUT": 300,
    }
}

# ============================================================
# Email Configuration
# ============================================================

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST")
EMAIL_PORT = config("EMAIL_PORT", cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool, default=True)
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL")

# ============================================================
# Static and Media Files
# ============================================================

# Use whitenoise for static files
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")  # noqa: F405
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media files storage (use cloud storage in production)
# Configure AWS S3 or similar for media files

# ============================================================
# Logging Configuration
# ============================================================

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "json": {
            "format": '{"level": "%(levelname)s", "time": "%(asctime)s", "module": "%(module)s", "message": "%(message)s"}',
        },
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "security": {
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "security.log",  # noqa: F405
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console", "mail_admins"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["security", "mail_admins"],
            "level": "WARNING",
            "propagate": False,
        },
        "security": {
            "handlers": ["security"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}

# ============================================================
# Allauth Configuration
# ============================================================

ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"
ACCOUNT_EMAIL_VERIFICATION = "mandatory"

# ============================================================
# REST Framework - Production Settings
# ============================================================

REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [  # noqa: F405
    "rest_framework.renderers.JSONRenderer",
]

REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {  # noqa: F405
    "anon": "50/hour",
    "user": "500/hour",
}

# ============================================================
# Admin Security
# ============================================================

# Change admin URL path
ADMIN_URL = config("ADMIN_URL", default="admin/")

# ============================================================
# Performance Optimizations
# ============================================================

# Template caching
TEMPLATES[0]["APP_DIRS"] = False  # Must disable when using custom loaders  # noqa: F405
TEMPLATES[0]["OPTIONS"]["loaders"] = [  # noqa: F405
    (
        "django.template.loaders.cached.Loader",
        [
            "django.template.loaders.filesystem.Loader",
            "django.template.loaders.app_directories.Loader",
        ],
    ),
]

# Remove debug option from templates
TEMPLATES[0]["OPTIONS"].pop("debug", None)  # noqa: F405
