"""
Configuraciones globales de la aplicación
"""
import os
from datetime import timedelta

# Entorno de ejecución
ENV = os.environ.get('FLASK_ENV', 'development')
DEBUG = ENV == 'development'
TESTING = os.environ.get('TESTING', 'false').lower() == 'true'

# Configuración de Base de Datos
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_NAME = os.environ.get('DB_NAME', 'visitor_registration')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'postgres')

# Construir URI de la base de datos según el entorno
if ENV == 'development' and not TESTING:
    # En desarrollo, usar SQLite por defecto si no se especifica otra cosa
    if os.environ.get('USE_SQLITE', 'true').lower() == 'true':
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///dev.db')
    else:
        SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
elif TESTING:
    # En pruebas, usar SQLite en memoria
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL', 'sqlite:///:memory:')
else:
    # En producción, usar la base de datos configurada
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# Configuración de SQLAlchemy
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = DEBUG

# Configuración de JWT
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'super-secret-key-for-development-only')
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

# Seguridad
MAX_LOGIN_ATTEMPTS = int(os.environ.get('MAX_LOGIN_ATTEMPTS', 5))
ACCOUNT_LOCKOUT_MINUTES = int(os.environ.get('ACCOUNT_LOCKOUT_MINUTES', 15))
PASSWORD_RESET_EXPIRY_HOURS = int(os.environ.get('PASSWORD_RESET_EXPIRY_HOURS', 24))
PASSWORD_MIN_LENGTH = int(os.environ.get('PASSWORD_MIN_LENGTH', 8))

# Configuración de correo electrónico
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_USERNAME = os.environ.get('SMTP_USERNAME', '')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
EMAIL_FROM = os.environ.get('EMAIL_FROM', 'noreply@centroculturalbanreservas.com')
EMAIL_ENABLED = os.environ.get('EMAIL_ENABLED', 'false').lower() == 'true'

# URLs de la aplicación
API_URL = os.environ.get('API_URL', 'http://localhost:5000')
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')

# Configuración de CORS
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')

# Configuración de archivos
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads'))
MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16 MB por defecto

# Límites de API
RATE_LIMIT_DEFAULT = os.environ.get('RATE_LIMIT_DEFAULT', '200 per hour')
RATE_LIMIT_AUTH = os.environ.get('RATE_LIMIT_AUTH', '5 per minute')

# Configuración de logs
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
LOG_FORMAT = os.environ.get('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
LOG_FILE = os.environ.get('LOG_FILE', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'app.log'))

# Crear directorios necesarios
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configuración específica para kioscos
KIOSK_HEARTBEAT_TIMEOUT_MINUTES = int(os.environ.get('KIOSK_HEARTBEAT_TIMEOUT_MINUTES', 5))
KIOSK_IDLE_TIMEOUT_SECONDS = int(os.environ.get('KIOSK_IDLE_TIMEOUT_SECONDS', 60)) 