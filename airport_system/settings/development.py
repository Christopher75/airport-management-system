"""
Django development settings for airport_system project.

Settings specific to local development environment.
"""

from .base import *  # noqa: F401, F403

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

# Database
# SQLite for easy development setup
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }
}

# Email - Console backend for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Django Debug Toolbar (optional - enable when installed)
try:
    import debug_toolbar  # noqa: F401

    INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405
    INTERNAL_IPS = ["127.0.0.1"]
except ImportError:
    pass

# Django Extensions (optional - enable when installed)
try:
    import django_extensions  # noqa: F401

    INSTALLED_APPS += ["django_extensions"]  # noqa: F405
except ImportError:
    pass

# Allauth - Use HTTP in development
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "http"

# Disable email verification for easier testing (optional)
# ACCOUNT_EMAIL_VERIFICATION = "optional"

# CORS - Allow all origins in development
CORS_ALLOW_ALL_ORIGINS = True

# Cache - Use local memory cache in development
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}

# Logging - More verbose in development
LOGGING["root"]["level"] = "DEBUG"  # noqa: F405
LOGGING["loggers"]["django"]["level"] = "DEBUG"  # noqa: F405
