from pathlib import Path
from dotenv import load_dotenv
import os

# Load .env variables
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / '.env')

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-u+#r&785v2*i=0z@28^af7x9$b5ghfjal_a-c-!41-vtz4*45b')

DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    '4cab-91-186-251-209.ngrok-free.app',
    'LoayAlzaben.pythonanywhere.com',
    'gaming-studio.onrender.com',  
]
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'studio',
    'crispy_forms',
    'crispy_bootstrap4',
    # ALL AUTHENTICATION APPS REMOVED!
]

CRISPY_TEMPLATE_PACK = 'bootstrap4'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # ALLAUTH MIDDLEWARE REMOVED!
]

ROOT_URLCONF = 'gaming_studio.urls'

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

WSGI_APPLICATION = 'gaming_studio.wsgi.application'

# Database configuration
if os.getenv('DEPLOY_ENV') == 'pythonanywhere':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'gaming_studio_db'),
            'USER': os.getenv('DB_USER', 'LoayAlzaben'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'your-postgres-password'),
            'HOST': os.getenv('DB_HOST', 'LoayAlzaben-1234.postgres.pythonanywhere-services.com'),
            'PORT': os.getenv('DB_PORT', '11234'),
        }
    }
else:
    # Use SQLite for local and Render deployments
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ...ex

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"

# Static files optimization for production
if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Logging configuration for production debugging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # For development - prints to console
DEFAULT_FROM_EMAIL = 'Gaming Studio <noreply@gaming-studio.com>'
EMAIL_HOST_USER = 'Gaming Studio'

# For production, you would use:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

# Authentication Settings
SITE_ID = 1

# Authentication backends - ALLAUTH REMOVED!
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

# ALL AUTHENTICATION CONFIGURATION REMOVED!
# NO MORE LOGIN/LOGOUT REDIRECTS
# NO MORE ALLAUTH SETTINGS
# SITE IS NOW COMPLETELY OPEN!