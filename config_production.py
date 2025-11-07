"""
Configuración para producción en AWS
"""
import os

# Detectar si estamos en producción
IS_PRODUCTION = os.environ.get('ENVIRONMENT', 'development') == 'production'

# Configuración de Flask
DEBUG = not IS_PRODUCTION
HOST = '0.0.0.0'
PORT = int(os.environ.get('PORT', 8080))

# Configuración de Chrome para producción (headless)
CHROME_OPTIONS = {
    'headless': IS_PRODUCTION,  # Headless en producción
    'no_sandbox': IS_PRODUCTION,  # Requerido en Docker/AWS
    'disable_dev_shm': IS_PRODUCTION,  # Evita problemas de memoria compartida
}

# Timeouts más largos en producción
SCRAPER_TIMEOUT = 900  # 15 minutos
PAGE_LOAD_TIMEOUT = 60

# Logging
LOG_LEVEL = 'INFO' if IS_PRODUCTION else 'DEBUG'
