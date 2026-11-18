"""F2 local skeleton settings. Not production deployment approval."""
import os
from pathlib import Path

from .environment import load_environment

BASE_DIR = Path(__file__).resolve().parent.parent
_configuration = load_environment(os.environ)
LOCAL_MODE = _configuration["local"]
DEBUG = _configuration["debug"]
SECRET_KEY = _configuration["secret"]
ALLOWED_HOSTS = _configuration["hosts"]
DATABASES = {"default": _configuration["database"]}
del _configuration

ROOT_URLCONF = "config.urls"
ASGI_APPLICATION = "config.asgi.application"
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "rest_framework",
    "modules.identity",
    "modules.access",
    "modules.usage",
    "modules.operations",
    "modules.ingestion",
]
MIDDLEWARE = [
    "modules.core.middleware.RequestPolicyMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework.authentication.SessionAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
}
LANGUAGE_CODE = "ar"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
STATIC_URL = "/static/"
WEB_DIST_DIR = BASE_DIR.parent / "web" / "dist"
APPEND_SLASH = False

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = not LOCAL_MODE
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = not LOCAL_MODE
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_TRUSTED_ORIGINS = []
CSRF_FAILURE_VIEW = "modules.core.views.csrf_failure"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "no-referrer"
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"
SECURE_SSL_REDIRECT = not LOCAL_MODE
SECURE_HSTS_SECONDS = 0 if LOCAL_MODE else 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = not LOCAL_MODE
SECURE_HSTS_PRELOAD = False
X_FRAME_OPTIONS = "DENY"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"metadata": {"()": "modules.core.logging.MetadataOnlyFormatter"}},
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "metadata"}},
    "root": {"handlers": ["console"], "level": "WARNING"},
    "loggers": {
        name: {"handlers": ["console"], "level": "WARNING", "propagate": False}
        for name in ("django.request", "django.server", "django.security")
    },
}
