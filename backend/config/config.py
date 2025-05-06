"""
Configuración de la aplicación
"""
import os
from datetime import timedelta

# Configuración básica
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-insegura-cambiar-en-produccion')
SERVER_NAME = os.environ.get('SERVER_NAME', None)

# Configuración de JWT
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

# Configuración de base de datos
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Configuración de Celery
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
