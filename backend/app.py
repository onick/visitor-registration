"""
Aplicación principal para la API del Centro Cultural Banreservas
"""
import os
from flask import Flask
from flask_cors import CORS
from flask_restx import Api
from flask_jwt_extended import JWTManager
from models.database import db
from api.endpoints import namespaces
import logging
from config.settings import *  # Importar directamente las variables de settings
from utils.validators import configure_validators
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from services.auth_service import AuthService

def create_app(config_override=None):
    """
    Crea y configura la aplicación Flask
    
    Args:
        config_override (dict, opcional): Configuraciones para sobrescribir
        
    Returns:
        app: Aplicación Flask configurada
    """
    app = Flask(__name__)
    
    # Cargar configuraciones desde variables importadas
    app.config['ENV'] = ENV
    app.config['DEBUG'] = DEBUG
    app.config['TESTING'] = TESTING
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
    app.config['SQLALCHEMY_ECHO'] = SQLALCHEMY_ECHO
    app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = JWT_ACCESS_TOKEN_EXPIRES
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = JWT_REFRESH_TOKEN_EXPIRES
    app.config['CORS_ORIGINS'] = CORS_ORIGINS
    app.config['RATE_LIMIT_DEFAULT'] = RATE_LIMIT_DEFAULT
    app.config['RATE_LIMIT_AUTH'] = RATE_LIMIT_AUTH
    app.config['LOG_LEVEL'] = LOG_LEVEL
    app.config['LOG_FORMAT'] = LOG_FORMAT
    app.config['LOG_FILE'] = LOG_FILE
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_IDENTITY_CLAIM'] = 'sub'
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'
    
    # Sobrescribir configuraciones si se proporcionan
    if config_override:
        app.config.update(config_override)
    
    # Configurar logging
    configure_logging(app)
    
    # Configurar CORS
    CORS(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}})
    
    # Configurar base de datos
    db.init_app(app)
    
    # Configurar JWT
    jwt = JWTManager(app)
    
    # Configurar rate limiting
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=[app.config['RATE_LIMIT_DEFAULT']],
        storage_uri="memory://"
    )
    
    # Configurar validadores
    configure_validators(app)
    
    # Configurar API
    api = Api(
        app,
        version='1.0',
        title='API de Registro de Visitantes',
        description='API para el sistema de registro de visitantes del Centro Cultural Banreservas',
        doc='/api/docs',
        prefix='/api/v1'
    )
    
    # Registrar namespaces
    for namespace in namespaces:
        api.add_namespace(namespace)
    
    # Crear rutas básicas
    @app.route('/')
    def index():
        return {
            'name': 'API de Registro de Visitantes - Centro Cultural Banreservas',
            'version': '1.0',
            'documentation': '/api/docs'
        }
    
    # Configurar manejadores de errores
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Recurso no encontrado'}, 404
    
    @app.errorhandler(500)
    def server_error(error):
        app.logger.error(f"Error del servidor: {error}")
        return {'error': 'Error interno del servidor'}, 500
    
    # Aplicar limitador de tasa a endpoints de autenticación
    for route in ['/api/v1/auth/login', '/api/v1/auth/register', '/api/v1/auth/password-reset-request']:
        limiter.limit(app.config['RATE_LIMIT_AUTH'])(app.route(route))
    
    return app

def configure_logging(app):
    """
    Configura el sistema de logging de la aplicación
    
    Args:
        app: Aplicación Flask
    """
    # Configurar el nivel de logging desde la configuración
    log_level = getattr(logging, app.config['LOG_LEVEL'])
    
    # Configurar formato de logs
    log_format = app.config['LOG_FORMAT']
    formatter = logging.Formatter(log_format)
    
    # Configurar handler para archivo
    if not app.config['TESTING']:
        file_handler = logging.FileHandler(app.config['LOG_FILE'])
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        app.logger.addHandler(file_handler)
    
    # Configurar handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    app.logger.addHandler(console_handler)
    
    # Establecer nivel de logger de la aplicación
    app.logger.setLevel(log_level)
    
    # Evitar propagación a los manejadores de logging predeterminados de Flask
    app.logger.propagate = False

if __name__ == '__main__':
    app = create_app()
    app.run(
        host=os.environ.get('HOST', '0.0.0.0'),
        port=int(os.environ.get('PORT', 5000)),
        debug=DEBUG
    )
