from datetime import timedelta
from dotenv import load_dotenv
from pathlib import Path
import logging
import os
import sys


load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# Never ship a hardcoded key. Required in every non-debug environment.
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = 'django-insecure-dev-only-do-not-use-in-production'
    else:
        raise RuntimeError("SECRET_KEY environment variable is required when DEBUG=False")

# Application-level field-encryption key (Fernet) for ENC columns (DOB, notes,
# MFA secret, weight…). Required in production; in DEBUG we derive a stable key
# from SECRET_KEY so local/test data stays readable without extra config.
FIELD_ENCRYPTION_KEY = os.environ.get('FIELD_ENCRYPTION_KEY')
if not FIELD_ENCRYPTION_KEY:
    if DEBUG:
        import base64 as _b64, hashlib as _hashlib
        FIELD_ENCRYPTION_KEY = _b64.urlsafe_b64encode(
            _hashlib.sha256(SECRET_KEY.encode()).digest()
        ).decode()
    else:
        raise RuntimeError("FIELD_ENCRYPTION_KEY environment variable is required when DEBUG=False")

ALLOWED_HOSTS = [h for h in os.environ.get('ALLOWED_HOSTS', '').split(',') if h]
if not ALLOWED_HOSTS:
    # Permissive only in local development; production must set ALLOWED_HOSTS.
    ALLOWED_HOSTS = ['*'] if DEBUG else []

# Behind Render's TLS-terminating proxy, trust the forwarded scheme so Django
# knows requests are HTTPS (needed for secure cookies + admin login).
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# CSRF trusted origins (scheme + host) — required for admin/session POST over
# HTTPS on Django 4+. The Render hostname is appended below when present.
CSRF_TRUSTED_ORIGINS = [o for o in os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',') if o]

# CORS: wide-open only in local dev. Production reads an explicit allowlist.
CORS_ALLOWED_ORIGINS = [o for o in os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',') if o]
CORS_ALLOW_ALL_ORIGINS = DEBUG and not CORS_ALLOWED_ORIGINS
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = (
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
)

CORS_ALLOW_HEADERS = (
    "accept",
    "authorization",
    "content-type",
    "user-agent",
    "x-csrftoken",
    "x-refresh-token",
    "x-requested-with",
)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.auth_app',
    'apps.common_app',
    'apps.settings_app',
    'apps.notifications_app'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'HN_COB_BE.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'HN_COB_BE.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get("DATABASE_NAME"),
        'USER': os.environ.get("DATABASE_USER"),
        'PASSWORD': os.environ.get("DATABASE_PASSWORD"),
        # Accept either name; DATABASE_HOSTNAME kept for backward compat.
        'HOST': os.environ.get("DATABASE_HOST") or os.environ.get("DATABASE_HOSTNAME"),
        'PORT': os.environ.get("DATABASE_PORT"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'

MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.console.EmailBackend',
    },
}


# ANSI escape codes for colors
COLORS = {
    "HEADER": "\033[95m",
    "OKBLUE": "\033[94m",
    "OKCYAN": "\033[96m",
    "OKGREEN": "\033[92m",
    "WARNING": "\033[93m",
    "FAIL": "\033[91m",
    "ENDC": "\033[0m",
    "BOLD": "\033[1m",
    "UNDERLINE": "\033[4m",
}

def setup_logging():
    logger = logging.getLogger(__name__)
    # Create logger
    logger.setLevel(logging.DEBUG)
    # Create console handler and set level to debug
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    # Create formatter with colored output
    class ColoredFormatter(logging.Formatter):
        def format(self, record):
            log_color = ""
            if record.levelname == "DEBUG":
                log_color = COLORS["OKBLUE"]
            elif record.levelname == "INFO":
                log_color = COLORS["OKGREEN"]
            elif record.levelname == "WARNING":
                log_color = COLORS["WARNING"]
            elif record.levelname == "ERROR":
                log_color = COLORS["FAIL"]
            elif record.levelname == "CRITICAL":
                log_color = COLORS["FAIL"] + COLORS["BOLD"]
            msg = super().format(record)
            return (
                f"{log_color}"
                f"{record.pathname}:{record.lineno} | function: {record.funcName}()\n"
                f"[{record.levelname}] | {msg}"
                f"{COLORS['ENDC']}\n"
            )
    formatter = ColoredFormatter("%(asctime)s - %(message)s")
    # Add formatter to console handler
    console_handler.setFormatter(formatter)
    # Add console handler to logger
    logger.addHandler(console_handler)
    return logger

logger = setup_logging()


try:
    """DATABASE CONFIG"""
    # These are kept for local development if needed, but DATABASES['default'] uses DATABASE_URL
    DATABASE_NAME = os.environ.get("DATABASE_NAME")
    DATABASE_USER = os.environ.get("DATABASE_USER")
    DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")
    DATABASE_HOST = os.environ.get("DATABASE_HOST")
    DATABASE_PORT = os.environ.get("DATABASE_PORT")

    """SENDGRID API"""
    SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")

    """FRONTEND URL"""
    FRONTEND_URL = os.environ.get("FRONTEND_URL")
    BACKEND_URL = os.environ.get("BACKEND_URL")

    """SUPPORT EMAIL"""
    SUPPORT_EMAIL = os.environ.get("SUPPORT_EMAIL")

except Exception as ex:
    logger.error("ERROR: ENVIRONMENT VARIABLE ERROR!!! CHECK YOUR .env file")
    logger.warning(ex)
