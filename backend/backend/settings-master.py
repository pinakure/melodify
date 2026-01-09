ANDROID = False
LINUX   = False
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
VERSION = '0.260106'
SECRET_KEY = 'django-insecure-x-xr0dk^wcis00z=aal_0@xx0z__+eviot4wt29-*%^uvp!i*8'
ALLOWED_HOSTS = [
    'melodify.com.82.223.13.41.nip.io',
    '.82.223.13.41.nip.io',
    '.nip.io',
    'localhost',
    '127.0.0.1',
    'melodify.com',
    'melodify.local',
]

INSTALLED_APPS = [
    'main',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'fontawesome_5'
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

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates' if not ANDROID else os.path.join(BASE_DIR, 'templates'),],
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

WSGI_APPLICATION = 'backend.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


LOG_FILE = '/var/log/melodify.log' if LINUX else os.path.join('..', 'melodify.log')

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend', 
    'main.auth_backends.NostrAuthBackend',     
]

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

if not DEBUG:
    STATIC_ROOT = '/static/melodify'
    if SECURE:
        SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
        SECURE_SSL_REDIRECT = True
        SESSION_COOKIE_SECURE = True
        CSRF_COOKIE_SECURE = True
        SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin-allow-popups"
        USE_X_FORWARDED_HOST = True
        CSRF_TRUSTED_ORIGINS = ['https://melodify.com.82.223.13.41.nip.io']
STATIC_FILES = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [ STATIC_FILES ]
STATIC_URL = 'static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
SPOTIFY_CLIENT_ID  = 'dc75272b15354119b9df60392848cc6a'
SPOTIFY_CLIENT_SECRET = '76d4dfef594f4625bd68b8068a574289' 
