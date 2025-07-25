from pathlib import Path
from dotenv import load_dotenv
import os

# Load .env variables
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / '.env')

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-u+#r&785v2*i=0z@28^af7x9$b5ghfjal_a-c-!41-vtz4*45b')

DEBUG = os.getenv('DEBUG', 'False') == 'True'

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
    'studio',
    'crispy_forms',
    'crispy_bootstrap4',
]

CRISPY_TEMPLATE_PACK = 'bootstrap4'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'gaming_studio.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
import sys
if 'gunicorn' in sys.argv[0]:
    import django
    django.setup()
    from django.core.management import call_command
    try:
        call_command('migrate', interactive=False)
        call_command('collectstatic', interactive=False, verbosity=0)
    except Exception as e:
        print(f"Startup management command error: {e}")