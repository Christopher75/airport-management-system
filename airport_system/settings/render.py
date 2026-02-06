"""
Django settings for Render.com deployment (free tier).

Inherits from base.py and configures for Render's environment:
- PostgreSQL via DATABASE_URL
- No Redis (uses local memory cache)
- WhiteNoise for static files
- Console-only logging (no file logging on ephemeral filesystem)
"""

from .base import *  # noqa: F401, F403

import dj_database_url
from decouple import config

# ============================================================
# Core Settings
# ============================================================

DEBUG = False

SECRET_KEY = config("SECRET_KEY")

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default=".onrender.com",
    cast=lambda v: [s.strip() for s in v.split(",") if s.strip()],
)

# Render provides the full URL, add it to CSRF trusted origins
RENDER_EXTERNAL_URL = config("RENDER_EXTERNAL_URL", default="")
if RENDER_EXTERNAL_URL:
    CSRF_TRUSTED_ORIGINS = [RENDER_EXTERNAL_URL]

# ============================================================
# Database - Render provides DATABASE_URL
# ============================================================

DATABASE_URL = config("DATABASE_URL", default="")
if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }

# ============================================================
# Static Files - WhiteNoise
# ============================================================

MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")  # noqa: F405
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ============================================================
# Security (Render handles SSL termination)
# ============================================================

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"

X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# HSTS - start with shorter duration, increase after confirming it works
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# ============================================================
# Cache - Local memory (no Redis on free tier)
# ============================================================

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "naia-render-cache",
    }
}

# Session engine - use database since no Redis
SESSION_ENGINE = "django.contrib.sessions.backends.db"

# ============================================================
# Email - Console for free tier (or SMTP if configured)
# ============================================================

EMAIL_BACKEND = config(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)

# If SMTP is configured, use it
if config("EMAIL_HOST_USER", default=""):
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
    EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
    EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
    EMAIL_HOST_USER = config("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")

# For development/free tier, make email verification optional
ACCOUNT_EMAIL_VERIFICATION = config(
    "ACCOUNT_EMAIL_VERIFICATION", default="optional"
)

# ============================================================
# Allauth - HTTPS protocol for Render
# ============================================================

ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"

# ============================================================
# REST Framework - Production Settings
# ============================================================

REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [  # noqa: F405
    "rest_framework.renderers.JSONRenderer",
]

# ============================================================
# Logging - Console only (Render captures stdout)
# ============================================================

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}

# ============================================================
# Performance - Template caching
# ============================================================

TEMPLATES[0]["OPTIONS"]["loaders"] = [  # noqa: F405
    (
        "django.template.loaders.cached.Loader",
        [
            "django.template.loaders.filesystem.Loader",
            "django.template.loaders.app_directories.Loader",
        ],
    ),
]
TEMPLATES[0]["OPTIONS"].pop("debug", None)  # noqa: F405

# ============================================================
# CORS
# ============================================================

CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default="",
    cast=lambda v: [s.strip() for s in v.split(",") if s.strip()],
)
if not CORS_ALLOWED_ORIGINS and RENDER_EXTERNAL_URL:
    CORS_ALLOWED_ORIGINS = [RENDER_EXTERNAL_URL]
