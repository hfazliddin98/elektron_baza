"""
Django settings for config project.

Elektron Baza — universitet qurilmalari ta'mirlash CRM tizimi.
Maxfiy sozlamalar .env faylidan o'qiladi (namuna: .env.example).
"""

import os
from pathlib import Path

from django.contrib.messages import constants as message_constants
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-dev-kalit')

DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

AUTH_USER_MODEL = 'accounts.User'


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Loyiha applari
    'accounts',
    'devices',
    'repairs',
    'reports',
    'bot',
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

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# .env da DB_NAME berilsa PostgreSQL, aks holda vaqtincha SQLite ishlatiladi

if os.getenv('DB_NAME'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME'),
            'USER': os.getenv('DB_USER', 'postgres'),
            'PASSWORD': os.getenv('DB_PASSWORD', ''),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation

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


# Internationalization

LANGUAGE_CODE = 'uz'

TIME_ZONE = 'Asia/Tashkent'

USE_I18N = True

USE_TZ = True


# Static va media fayllar

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'


# Autentifikatsiya yo'nalishlari (5-bosqichda ishlatiladi)

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

# Bootstrap'da xato uslubi "danger" deb ataladi
MESSAGE_TAGS = {message_constants.ERROR: 'danger'}


# Telegram bot (10-bosqichda ishlatiladi)

BOT_TOKEN = os.getenv('BOT_TOKEN', '')
BOT_ADMIN_CHAT = os.getenv('BOT_ADMIN_CHAT', '')   # operator/admin guruhi chat_id
SAYT_MANZILI = os.getenv('SAYT_MANZILI', 'http://127.0.0.1:8000')


# Ishlab chiqarish (production) xavfsizligi — faqat DEBUG=False bo'lganda

CSRF_TRUSTED_ORIGINS = [
    manzil.strip() for manzil in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',')
    if manzil.strip()
]

if not DEBUG:
    # HTTPS bo'lmagan ichki serverda .env da HTTPS=False qiling
    https = os.getenv('HTTPS', 'True') == 'True'
    SECURE_SSL_REDIRECT = https
    SESSION_COOKIE_SECURE = https
    CSRF_COOKIE_SECURE = https
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_HSTS_SECONDS = 31536000 if https else 0
    SECURE_HSTS_INCLUDE_SUBDOMAINS = https
    SECURE_HSTS_PRELOAD = https
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'


# Loglash — LOG_FAYL sozlansa, faylga ham yoziladi

LOG_FAYL = os.getenv('LOG_FAYL', '')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'oddiy': {'format': '{asctime} {levelname} {name}: {message}', 'style': '{'},
    },
    'handlers': {
        'konsol': {'class': 'logging.StreamHandler', 'formatter': 'oddiy'},
        **({'fayl': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_FAYL,
            'maxBytes': 5 * 1024 * 1024,
            'backupCount': 5,
            'formatter': 'oddiy',
        }} if LOG_FAYL else {}),
    },
    'root': {
        'handlers': ['konsol'] + (['fayl'] if LOG_FAYL else []),
        'level': 'INFO',
    },
}
