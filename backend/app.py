"""
Aplicación Flask mejorada con soporte para múltiples bases de datos
"""
import os
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from models.database import db, init_app
from models.visitor import Visitor, VisitorCheckIn
from models.event import Event
from models.user import User
from models.kiosk import Kiosk
from models.notification import Notification
from config.database_config import config
from dotenv import load_dotenv
from api.dashboard_analytics import init_dashboard_analytics
from api.export_endpoint import export_bp
from api.upload_endpoint import upload_bp
from api.visitors_api import visitors_bp
from flask import send_from_directory

# Cargar variables de entorno
load_dotenv()

from flask_jwt_extended import JWTManager
from backend.errors import register_jwt_error_handlers
from flask_restx import Api
from backend.api.endpoints.auth import auth_namespace
from backend.api.endpoints.events import events_namespace
from backend.api.endpoints.kiosks import kiosks_namespace
from backend.api.endpoints.notifications import notifications_namespace
from backend.api.endpoints.visitors import visitors_namespace


def create_app(config_name=None):
    """Crear y configurar la aplicación Flask"""
    app = Flask(__name__)
    
    # Seleccionar configuración basada en el ambiente
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # Sobrescribir con DATABASE_URL si está presente en el entorno
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    
    # Inicializar extensiones
    CORS(app)
    init_app(app)  # Inicializa SQLAlchemy
    
    # Configurar JWT
    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "super-secret-fallback") # Fallback por si no está en .env
    jwt = JWTManager(app)
    register_jwt_error_handlers(jwt)

    # Configurar Flask-RestX API
    api = Api(
        app,
        version='1.0',
        title='CCB API',
        description='API para el Centro Cultural Banreservas',
        doc='/api/docs',
        prefix='/api/v1'  # Prefijo común para todos los namespaces
    )

    api.add_namespace(auth_namespace, path='/auth')
    api.add_namespace(events_namespace, path='/events')
    api.add_namespace(kiosks_namespace, path='/kiosks')
    api.add_namespace(notifications_namespace, path='/notifications')
    api.add_namespace(visitors_namespace, path='/visitors')
    
    return app

app = create_app()

# Inicializar endpoints de analytics (si aún es relevante o si no es cubierto por RestX)
init_dashboard_analytics(app)

# Registrar blueprint de exportación (Si no se maneja con RestX)
# app.register_blueprint(export_bp)

# Registrar blueprint de uploads (Si no se maneja con RestX)
# app.register_blueprint(upload_bp)

# Registrar blueprint de API de visitantes avanzada (Si no se maneja con RestX)
# app.register_blueprint(visitors_bp)

# Las rutas Flask estándar (@app.route) para /api/v1/... podrían necesitar ser removidas o 
# refactorizadas si entran en conflicto con los namespaces de Flask-RestX.
# Por ejemplo, la ruta @app.route("/api/v1/auth/login", methods=["POST"]) ahora está cubierta por auth_namespace.

# ========================
# RUTA DE ARCHIVOS ESTÁTICOS (Mantener si es necesario)
# ========================
@app.route('/uploads/<path:folder>/<path:filename>')
def serve_upload(folder, filename):
    """Servir archivos subidos"""
    upload_path = os.path.join(os.getcwd(), 'backend', 'uploads', folder)
    return send_from_directory(upload_path, filename)

# ========================
# RUTA DE INICIO (Puede modificarse para reflejar la estructura de API con RestX)
# ========================
# Esta ruta de inicio puede ser reemplazada o complementada por la documentación de Swagger UI en /api/docs
@app.route("/")
def index():
    """Página de inicio del API"""
    return jsonify({
        "message": "API del Sistema de Registro de Visitantes CCB",
        "version": "1.0",
        "documentation": "/api/docs", # Enlace a la documentación de Swagger
        "status": "online",
        "database": "PostgreSQL" # Esto podría ser dinámico o basado en config
    })

# Se eliminan los endpoints de Flask estándar que serán manejados por Flask-RestX
# para evitar conflictos. Por ejemplo, el endpoint /api/v1/auth/login
# ahora será manejado por el auth_namespace.
# Los endpoints de /api/v1/events/* serán manejados por events_namespace.
# Los endpoints de /api/v1/visitors/* serán manejados por visitors_namespace.

# ========================
# INICIALIZACIÓN (Mantener si es necesario para la ejecución directa)
# ========================
def init_db():
    """Inicializar base de datos con datos de prueba"""
    with app.app_context():
        db.create_all()
        
        # Crear evento de prueba si no hay eventos
        if Event.query.count() == 0:
            event = Event(
                title="Recital de Poesía",
                description="Lectura de poemas de autores dominicanos",
                start_date=datetime(2025, 5, 20, 18, 0),
                end_date=datetime(2025, 5, 20, 20, 0),
                location="Sala de Conferencias",
                is_active=True
            )
            db.session.add(event)
            db.session.commit()
            print("Evento de prueba creado")

if __name__ == "__main__":
    # La inicialización de la BD podría ser manejada por un script separado o un comando CLI de Flask
    # init_db() 
    app.run(host='0.0.0.0', port=8080, debug=True)
