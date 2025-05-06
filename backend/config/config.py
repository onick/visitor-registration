"""
Configuración de la aplicación
"""
import os
from datetime import timedelta

# Configuración de la base de datos
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@db:5432/visitor_db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Configuración general
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
SERVER_NAME = os.environ.get('SERVER_NAME', None)

# Configuración de archivos
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

# Configuración de JWT
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

# Configuración de correo
MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.example.com')
MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'no-reply@ccb.do')

# Configuración de seguridad
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')

# Configuración de Celery
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')
