"""
Aplicación principal para la API del Centro Cultural Banreservas
"""
import os
from flask import Flask
from flask_cors import CORS
from flask_restx import Api

def create_app(config=None):
    """
    Factory de aplicación Flask
    """
    app = Flask(__name__)
    
    # Configuración desde variables de entorno
    app.config.from_pyfile('config/config.py')
    
    # Sobreescribir configuración si se proporciona
    if config:
        app.config.update(config)
    
    # Inicializar CORS
    CORS(app)
    
    # Inicializar API
    api = Api(
        app,
        version='1.0',
        title='Centro Cultural Banreservas API',
        description='API para el sistema de gestión de eventos y kioscos',
        prefix='/api/v1'
    )
    
    # Importar y registrar endpoints
    from api.endpoints.events import events_namespace
    from api.endpoints.visitors import visitors_namespace
    from api.endpoints.kiosks import kiosks_namespace
    
    api.add_namespace(events_namespace)
    api.add_namespace(visitors_namespace)
    api.add_namespace(kiosks_namespace)
    
    # Registrar manejadores de errores
    register_error_handlers(app)
    
    return app

def register_error_handlers(app):
    """
    Registra manejadores de errores para la aplicación
    """
    @app.errorhandler(404)
    def handle_404_error(error):
        return {"error": "Recurso no encontrado"}, 404
    
    @app.errorhandler(500)
    def handle_500_error(error):
        return {"error": "Error interno del servidor"}, 500

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
