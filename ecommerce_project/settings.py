"""
Django Settings for ecommerce_project
=======================================
Simple, beginner-friendly settings file.
MongoDB Atlas is used as the database.
"""

import os
from pathlib import Path
import environ
import dj_database_url

# ─────────────────────────────────────────
# Build paths inside the project like:
# BASE_DIR / 'subdir'
# ─────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# ─────────────────────────────────────────
# Load variables from .env file
# ─────────────────────────────────────────
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# ─────────────────────────────────────────
# SECRET KEY & DEBUG
# ─────────────────────────────────────────
SECRET_KEY = env('SECRET_KEY', default='django-insecure-fallback-key-change-me')
DEBUG = env.bool('DEBUG', default=True)
ALLOWED_HOSTS = ['*']  # Allow all hosts (for development & Vercel)

# --- VERCEL PRODUCTION SECURITY ---
# Tell Django that Vercel is using HTTPS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# CSRF Trusted Origins for Vercel & Local Dev
# This is REQUIRED for POST requests (like Delete/Add Product) to work on HTTPS
CSRF_TRUSTED_ORIGINS = [
    'https://*.vercel.app',
    'https://*.now.sh',
    'http://127.0.0.1:8000',
    'http://localhost:8000',
]

# ─────────────────────────────────────────
# INSTALLED APPS
# These are the apps Django uses.
# 'store' is our custom shopping app.
# ─────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'store',  # Our custom store app
]

# ─────────────────────────────────────────
# MIDDLEWARE
# Middleware processes requests/responses.
# ─────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',   # For static files on Vercel
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # Custom Middleware for profile forcing
    'store.middleware.ProfileCompletionMiddleware',
]

# Google Maps API Key (from .env)
GOOGLE_MAPS_API_KEY = env('GOOGLE_MAPS_API_KEY', default='')

ROOT_URLCONF = 'ecommerce_project.urls'

# ─────────────────────────────────────────
# TEMPLATES
# HTML templates configuration.
# ─────────────────────────────────────────
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Our templates folder
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'store.context_processors.cart_count_processor',  # Custom cart counter
            ],
        },
    },
]

WSGI_APPLICATION = 'ecommerce_project.wsgi.application'

# ─────────────────────────────────────────
# DATABASE
# We use SQLite for Django's built-in
# auth/session system, and MongoDB Atlas
# for our products & cart data.
# ─────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# If running on Vercel (POSTGRES_URL is present), switch to Postgres
if 'POSTGRES_URL' in os.environ:
    DATABASES['default'] = dj_database_url.config(
        default=os.environ.get('POSTGRES_URL'),
        conn_max_age=600,
        ssl_require=True
    )

# MongoDB Atlas Connection (using pymongo directly)
MONGO_URI = env('MONGO_URI', default='')
MONGO_DB_NAME = env('MONGO_DB_NAME', default='ecommerce_db')

# ─────────────────────────────────────────
# PASSWORD VALIDATION
# ─────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─────────────────────────────────────────
# INTERNATIONALIZATION
# ─────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'   # Indian Standard Time
USE_I18N = True
USE_TZ = True

# ─────────────────────────────────────────
# STATIC FILES (CSS, JavaScript, Images)
# ─────────────────────────────────────────
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# ─────────────────────────────────────────
# MEDIA FILES (Uploaded images)
# ─────────────────────────────────────────
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ─────────────────────────────────────────
# DEFAULT PRIMARY KEY
# ─────────────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─────────────────────────────────────────
# LOGIN / LOGOUT REDIRECT
# ─────────────────────────────────────────
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
