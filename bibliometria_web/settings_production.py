"""
Configuración de settings para producción en Google Cloud
Uso: export DJANGO_SETTINGS_MODULE=bibliometria_web.settings_production
"""
from .settings import *
import os

# SEGURIDAD
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY', 'CHANGE-ME-IN-PRODUCTION')

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.run.app',  # Cloud Run
    '.cloudrun.app',  # Cloud Run
    # Agregar tu dominio aquí
]

# CSRF
CSRF_TRUSTED_ORIGINS = [
    'https://*.run.app',
    'https://*.cloudrun.app',
    # Agregar tu dominio aquí
]

# CORS para frontend
CORS_ALLOWED_ORIGINS = [
    "https://tu-frontend.com",
]

# Base de datos (opcional - si decides usar CloudSQL)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.environ.get('DB_NAME'),
#         'USER': os.environ.get('DB_USER'),
#         'PASSWORD': os.environ.get('DB_PASSWORD'),
#         'HOST': os.environ.get('DB_HOST'),
#         'PORT': '5432',
#     }
# }

# Archivos estáticos
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Cloud Storage (opcional)
# DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
# GS_BUCKET_NAME = os.environ.get('GS_BUCKET_NAME')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
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
