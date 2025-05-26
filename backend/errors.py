"""
Manejo centralizado de errores de la aplicación
"""
from flask import jsonify, current_app
from werkzeug.exceptions import HTTPException
import traceback

# Códigos de error personalizados
ERROR_CODES = {
    # Errores de autenticación
    'AUTH_INVALID_CREDENTIALS': 'Credenciales inválidas',
    'AUTH_EXPIRED_TOKEN': 'Token expirado',
    'AUTH_INVALID_TOKEN': 'Token inválido',
    'AUTH_MISSING_TOKEN': 'Token requerido',
    'AUTH_ACCOUNT_LOCKED': 'Cuenta bloqueada',
    
    # Errores de autorización
    'FORBIDDEN': 'No tiene permisos para realizar esta acción',
    'PERMISSION_DENIED': 'Permiso denegado',
    
    # Errores de validación
    'VALIDATION_ERROR': 'Error de validación',
    'INVALID_INPUT': 'Datos de entrada inválidos',
    'MISSING_REQUIRED_FIELD': 'Campo requerido faltante',
    'INVALID_FORMAT': 'Formato inválido',
    
    # Errores de recursos
    'RESOURCE_NOT_FOUND': 'Recurso no encontrado',
    'RESOURCE_ALREADY_EXISTS': 'El recurso ya existe',
    'RESOURCE_CONFLICT': 'Conflicto con el recurso',
    
    # Errores de operación
    'OPERATION_FAILED': 'La operación ha fallado',
    'RATE_LIMIT_EXCEEDED': 'Límite de peticiones excedido',
    'DATABASE_ERROR': 'Error en la base de datos',
    'EXTERNAL_SERVICE_ERROR': 'Error en servicio externo',
    
    # Errores específicos del sistema
    'EVENT_FULL': 'El evento está lleno',
    'REGISTRATION_CLOSED': 'El registro está cerrado',
    'VISITOR_ALREADY_REGISTERED': 'El visitante ya está registrado',
    'VISITOR_ALREADY_CHECKED_IN': 'El visitante ya ha hecho check-in',
    
    # Errores del sistema
    'SYSTEM_ERROR': 'Error interno del sistema',
    'MAINTENANCE_MODE': 'Sistema en mantenimiento',

    # Errores JWT
    'AUTH_FRESH_TOKEN_REQUIRED': 'Se requiere un token fresco',
    'AUTH_CSRF_ERROR': 'Error de CSRF' # Aunque CSRFError no se manejará con un loader de jwt aquí
}

from flask_jwt_extended.exceptions import (
    ExpiredSignatureError,
    InvalidHeaderError,  # Usado para referencia, manejado por invalid_token_loader
    NoAuthorizationError, # Usado para referencia, manejado por unauthorized_loader
    WrongTokenError,  # Usado para referencia, manejado por invalid_token_loader
    RevokedTokenError,
    FreshTokenRequired,
    CSRFError  # No se manejará con un loader de jwt en register_jwt_error_handlers
)

def register_jwt_error_handlers(jwt):
    """
    Registra manejadores de errores específicos de JWT utilizando los decoradores de JWTManager.
    
    Args:
        jwt: Instancia de JWTManager
    """
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        """Manejador para tokens expirados."""
        return create_error_response('AUTH_EXPIRED_TOKEN', 'El token ha expirado'), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        """
        Manejador para tokens inválidos. Esto cubre varios escenarios como
        InvalidHeaderError y WrongTokenError. Se intenta diferenciar el mensaje
        basado en el error_string.
        """
        # Heurística para diferenciar el tipo de error de token inválido
        if 'header' in error_string.lower():
            # Corresponde a InvalidHeaderError
            message = 'Encabezado de autorización inválido'
        elif 'token type' in error_string.lower() or 'wrong type' in error_string.lower():
            # Corresponde a WrongTokenError
            message = 'Token incorrecto (ej. se esperaba access pero se recibió refresh)'
        else:
            # Mensaje genérico para otros errores de token inválido
            message = f'Token inválido o malformado: {error_string}'
        return create_error_response('AUTH_INVALID_TOKEN', message), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error_string):
        """Manejador para cuando falta el token de autorización (NoAuthorizationError)."""
        # error_string usualmente es algo como "Missing Authorization Header"
        return create_error_response('AUTH_MISSING_TOKEN', 'Token de autorización no encontrado'), 401

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        """Manejador para tokens que han sido revocados."""
        return create_error_response('AUTH_INVALID_TOKEN', 'El token ha sido revocado'), 401

    @jwt.needs_fresh_token_loader
    def fresh_token_required_callback(jwt_header, jwt_payload):
        """Manejador para cuando se requiere un token fresco pero se proporcionó uno no fresco."""
        return create_error_response('AUTH_FRESH_TOKEN_REQUIRED', 'Se requiere un token fresco'), 401

    # Nota: CSRFError no se maneja aquí porque flask-jwt-extended no proporciona
    # un decorador de JWTManager específico para ello (ej. @jwt.csrf_error_loader).
    # CSRFError típicamente se maneja a nivel de aplicación con @app.errorhandler(CSRFError).

def register_error_handlers(app):
    """
    Registra manejadores de errores en la aplicación Flask
    
    Args:
        app: Aplicación Flask
    """
    @app.errorhandler(400)
    def bad_request(e):
        return create_error_response('INVALID_INPUT', str(e)), 400
        
    @app.errorhandler(401)
    def unauthorized(e):
        return create_error_response('AUTH_INVALID_CREDENTIALS', str(e)), 401
        
    @app.errorhandler(403)
    def forbidden(e):
        return create_error_response('FORBIDDEN', str(e)), 403
        
    @app.errorhandler(404)
    def not_found(e):
        return create_error_response('RESOURCE_NOT_FOUND', str(e)), 404
        
    @app.errorhandler(405)
    def method_not_allowed(e):
        return create_error_response('INVALID_INPUT', f"Método {request.method} no permitido"), 405
        
    @app.errorhandler(409)
    def conflict(e):
        return create_error_response('RESOURCE_CONFLICT', str(e)), 409
        
    @app.errorhandler(422)
    def unprocessable_entity(e):
        return create_error_response('VALIDATION_ERROR', str(e)), 422
        
    @app.errorhandler(429)
    def too_many_requests(e):
        return create_error_response('RATE_LIMIT_EXCEEDED', str(e)), 429
        
    @app.errorhandler(500)
    def internal_server_error(e):
        # Registrar el error
        log_error(e)
        return create_error_response('SYSTEM_ERROR', "Error interno del servidor"), 500
        
    @app.errorhandler(Exception)
    def handle_exception(e):
        # Manejar excepciones no capturadas
        if isinstance(e, HTTPException):
            return jsonify({"status": "error", "code": "HTTP_ERROR", "message": e.description}), e.code
            
        # Registrar el error
        log_error(e)
        return create_error_response('SYSTEM_ERROR', "Error interno del servidor"), 500

def create_error_response(error_code, message=None, details=None):
    """
    Crea una respuesta de error estandarizada
    
    Args:
        error_code (str): Código de error
        message (str, optional): Mensaje de error personalizado
        details (dict, optional): Detalles adicionales del error
        
    Returns:
        dict: Respuesta de error
    """
    # Si no se proporciona mensaje, usar el mensaje predeterminado para el código
    if message is None:
        message = ERROR_CODES.get(error_code, "Error desconocido")
        
    response = {
        "status": "error",
        "code": error_code,
        "message": message
    }
    
    if details:
        response["details"] = details
        
    return jsonify(response)

def log_error(exception):
    """
    Registra un error en el log
    
    Args:
        exception: Excepción a registrar
    """
    error_traceback = traceback.format_exc()
    current_app.logger.error(f"Error: {str(exception)}\nTraceback: {error_traceback}")

def format_validation_errors(errors):
    """
    Formatea errores de validación de Marshmallow
    
    Args:
        errors (dict): Errores de validación
        
    Returns:
        dict: Detalles de errores formateados
    """
    details = {}
    
    for field, field_errors in errors.items():
        if isinstance(field_errors, list):
            details[field] = field_errors[0]
        elif isinstance(field_errors, dict):
            details[field] = format_validation_errors(field_errors)
        else:
            details[field] = str(field_errors)
            
    return details

class APIError(Exception):
    """
    Excepción personalizada para errores de API
    """
    def __init__(self, error_code, message=None, details=None, status_code=400):
        """
        Inicializa una excepción de API
        
        Args:
            error_code (str): Código de error
            message (str, optional): Mensaje de error personalizado
            details (dict, optional): Detalles adicionales del error
            status_code (int): Código de estado HTTP
        """
        self.error_code = error_code
        self.message = message or ERROR_CODES.get(error_code, "Error desconocido")
        self.details = details
        self.status_code = status_code
        
    def to_response(self):
        """
        Convierte la excepción a una respuesta HTTP
        
        Returns:
            tuple: (respuesta, código de estado)
        """
        return create_error_response(self.error_code, self.message, self.details), self.status_code 