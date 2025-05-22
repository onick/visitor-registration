"""
Configuración centralizada para la aplicación
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

# Cargar variables de entorno desde archivo .env
load_dotenv()

class Config:
    """Configuración base"""
    # Configuración general
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Configuración de base de datos
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///instance/dev.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Configuración de seguridad
    FORCE_HTTPS = os.environ.get('FORCE_HTTPS', 'False').lower() == 'true'
    MAX_LOGIN_ATTEMPTS = int(os.environ.get('MAX_LOGIN_ATTEMPTS', 5))
    ACCOUNT_LOCKOUT_MINUTES = int(os.environ.get('ACCOUNT_LOCKOUT_MINUTES', 15))
    PASSWORD_RESET_EXPIRY_HOURS = int(os.environ.get('PASSWORD_RESET_EXPIRY_HOURS', 24))
    
    # Configuración de rate limiting
    RATELIMIT_DEFAULT = "200 per day, 50 per hour"
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'memory://')
    RATELIMIT_HEADERS_ENABLED = True
    
    # Configuración de cache
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'SimpleCache')
    CACHE_REDIS_URL = os.environ.get('REDIS_URL', None)
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_TIMEOUT', 300))  # 5 minutos por defecto
    
    # Configuración de Celery
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', os.environ.get('REDIS_URL', 'redis://localhost:6379/0'))
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', os.environ.get('REDIS_URL', 'redis://localhost:6379/0'))
    
    # Configuración de correo electrónico
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'localhost')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 25))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'False').lower() == 'true'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', None)
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', None)
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@example.com')
    
    # Configuración de Sentry para monitoreo de errores
    SENTRY_DSN = os.environ.get('SENTRY_DSN', None)
    
    # Otras configuraciones
    UPLOADS_FOLDER = os.environ.get('UPLOADS_FOLDER', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads'))
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_UPLOAD_SIZE', 16 * 1024 * 1024))  # 16MB por defecto
    
    # Log de auditoría
    AUDIT_LOG_ENABLED = os.environ.get('AUDIT_LOG_ENABLED', 'True').lower() == 'true'

class DevelopmentConfig(Config):
    """Configuración para entorno de desarrollo"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///instance/dev.db')
    
    # Configuración de JWT para desarrollo (tokens más largos)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    
    # Configuración de rate limiting más permisiva para desarrollo
    RATELIMIT_DEFAULT = "1000 per day, 200 per hour"

class TestingConfig(Config):
    """Configuración para entorno de pruebas"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL', 'sqlite:///instance/test.db')
    
    # Desactivar rate limiting para pruebas
    RATELIMIT_ENABLED = False
    
    # Configuración de JWT para pruebas
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=3600)
    
    # Desactivar envío real de correos en pruebas
    MAIL_SUPPRESS_SEND = True

class ProductionConfig(Config):
    """Configuración para entorno de producción"""
    # Forzar HTTPS en producción
    FORCE_HTTPS = True
    
    # Asegurarse de que se ha establecido una clave secreta
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("No se ha establecido SECRET_KEY. Esta variable es obligatoria en producción.")
    
    # Validar configuración de base de datos
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("No se ha establecido DATABASE_URL. Esta variable es obligatoria en producción.")
    
    # Usar Redis para rate limiting en producción
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL')
    if not RATELIMIT_STORAGE_URL:
        raise ValueError("No se ha establecido REDIS_URL. Esta variable es obligatoria en producción.")
    
    # Usar Redis para caché en producción
    CACHE_TYPE = 'RedisCache'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL')
    
    # Validar configuración de correo en producción
    if not all([os.environ.get('MAIL_SERVER'), os.environ.get('MAIL_USERNAME'), os.environ.get('MAIL_PASSWORD')]):
        raise ValueError("Configuración de correo incompleta. MAIL_SERVER, MAIL_USERNAME y MAIL_PASSWORD son obligatorias en producción.")

# Mapear configuraciones a nombres de entorno
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    """
    Obtiene la configuración según el entorno
    """
    env = os.environ.get('FLASK_ENV', 'default')
    return config.get(env, config['default'])
