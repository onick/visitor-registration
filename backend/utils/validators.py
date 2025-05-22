"""
Validadores para datos de entrada en la API
"""
import re
from datetime import datetime, timedelta
from flask import request, jsonify
from functools import wraps
import html
import json
from marshmallow import Schema, fields, ValidationError

# Expresiones regulares para validaciones comunes
REGEX_EMAIL = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
REGEX_USERNAME = r'^[a-zA-Z0-9_-]{3,20}$'
REGEX_PASSWORD = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
REGEX_PHONE = r'^\+?[0-9]{7,15}$'
REGEX_NAME = r'^[a-zA-Z\s\-\'áéíóúÁÉÍÓÚüÜñÑ]{2,100}$'
REGEX_REGISTRATION_CODE = r'^[A-Z0-9]{6}$'

def validate_email(email):
    """
    Valida un correo electrónico
    
    Args:
        email (str): Correo electrónico a validar
        
    Returns:
        bool: True si es válido, False en caso contrario
    """
    if not email or not isinstance(email, str):
        return False
    return re.match(REGEX_EMAIL, email) is not None

def validate_username(username):
    """
    Valida un nombre de usuario
    
    Args:
        username (str): Nombre de usuario a validar
        
    Returns:
        bool: True si es válido, False en caso contrario
    """
    if not username or not isinstance(username, str):
        return False
    return re.match(REGEX_USERNAME, username) is not None

def validate_password(password):
    """
    Valida una contraseña
    
    Args:
        password (str): Contraseña a validar
        
    Returns:
        bool: True si es válida, False en caso contrario
    """
    if not password or not isinstance(password, str):
        return False
    return re.match(REGEX_PASSWORD, password) is not None

def validate_phone(phone):
    """
    Valida un número de teléfono
    
    Args:
        phone (str): Número de teléfono a validar
        
    Returns:
        bool: True si es válido, False en caso contrario
    """
    if not phone or not isinstance(phone, str):
        return False
    return re.match(REGEX_PHONE, phone) is not None

def validate_name(name):
    """
    Valida un nombre
    
    Args:
        name (str): Nombre a validar
        
    Returns:
        bool: True si es válido, False en caso contrario
    """
    if not name or not isinstance(name, str):
        return False
    return re.match(REGEX_NAME, name) is not None

def sanitize_html(text):
    """
    Sanitiza texto para prevenir XSS
    
    Args:
        text (str): Texto a sanitizar
        
    Returns:
        str: Texto sanitizado
    """
    if not text or not isinstance(text, str):
        return text
    return html.escape(text)

def sanitize_input(data):
    """
    Sanitiza todos los valores de texto en un diccionario o lista
    
    Args:
        data (dict/list): Datos a sanitizar
        
    Returns:
        dict/list: Datos sanitizados
    """
    if isinstance(data, dict):
        return {k: sanitize_input(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    elif isinstance(data, str):
        return sanitize_html(data)
    else:
        return data

# Schemas de Marshmallow para validación

class UserSchema(Schema):
    """Schema para validación de usuarios"""
    username = fields.Str(required=True, validate=lambda s: re.match(REGEX_USERNAME, s))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=lambda s: re.match(REGEX_PASSWORD, s))
    first_name = fields.Str(required=True, validate=lambda s: re.match(REGEX_NAME, s))
    last_name = fields.Str(required=True, validate=lambda s: re.match(REGEX_NAME, s))
    role = fields.Str(required=True, validate=lambda s: s in ['admin', 'staff'])

class VisitorSchema(Schema):
    """Schema para validación de visitantes"""
    name = fields.Str(required=True, validate=lambda s: re.match(REGEX_NAME, s))
    email = fields.Email(required=True)
    phone = fields.Str(required=True, validate=lambda s: re.match(REGEX_PHONE, s))

class EventSchema(Schema):
    """Schema para validación de eventos"""
    title = fields.Str(required=True, validate=lambda s: len(s) >= 3 and len(s) <= 100)
    description = fields.Str(required=True)
    location = fields.Str(required=True)
    start_date = fields.DateTime(required=True)
    end_date = fields.DateTime(required=True)
    capacity = fields.Int(required=True, validate=lambda n: n > 0)
    event_type = fields.Str(required=False)

class RegistrationSchema(Schema):
    """Schema para validación de registros"""
    visitor_id = fields.Int(required=True)
    event_id = fields.Int(required=True)
    registration_code = fields.Str(required=False, validate=lambda s: s is None or re.match(REGEX_REGISTRATION_CODE, s))
    status = fields.Str(required=False, validate=lambda s: s in ['REGISTERED', 'CHECKED_IN', 'NO_SHOW', 'CANCELED'])
    notes = fields.Str(required=False)

def validate_json_schema(data, schema_class):
    """
    Valida datos contra un schema de Marshmallow
    
    Args:
        data (dict): Datos a validar
        schema_class (Schema): Clase de schema a utilizar
        
    Returns:
        tuple: (bool, dict) - Éxito de validación y datos validados o errores
    """
    schema = schema_class()
    try:
        # Validar y deserializar
        validated_data = schema.load(data)
        return True, validated_data
    except ValidationError as err:
        return False, err.messages

def create_error_response(error_code, message, details=None):
    """
    Crea una respuesta de error estandarizada
    
    Args:
        error_code (str): Código de error
        message (str): Mensaje de error
        details (dict, optional): Detalles adicionales
        
    Returns:
        dict: Respuesta de error
    """
    response = {
        "status": "error",
        "code": error_code,
        "message": message
    }
    
    if details:
        response["details"] = details
        
    return response

def validate_date_range(start_date, end_date):
    """
    Validar rango de fechas
    """
    if start_date > end_date:
        return False
    
    # Eventos no pueden durar más de 7 días
    max_duration = timedelta(days=7)
    if end_date - start_date > max_duration:
        return False
    
    return True

def validate_required_fields(required_fields):
    """
    Decorador para validar campos requeridos en el cuerpo de la solicitud
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            data = request.json
            
            if not data:
                return jsonify(error="No se proporcionaron datos"), 400
            
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                return jsonify(error=f"Campos requeridos faltantes: {', '.join(missing_fields)}"), 400
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def validate_event_data(data):
    """
    Validar datos de un evento
    """
    errors = []
    
    # Título
    if 'title' in data:
        if len(data['title']) < 5:
            errors.append("El título debe tener al menos 5 caracteres")
    
    # Descripción
    if 'description' in data:
        if len(data['description']) < 10:
            errors.append("La descripción debe tener al menos 10 caracteres")
    
    # Fechas
    if 'start_date' in data and 'end_date' in data:
        try:
            start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
            
            if not validate_date_range(start_date, end_date):
                errors.append("Rango de fechas inválido")
        except ValueError:
            errors.append("Formato de fecha inválido")
    
    # Ubicación
    if 'location' in data:
        if len(data['location']) < 3:
            errors.append("La ubicación debe tener al menos 3 caracteres")
    
    return errors

def validate_visitor_data(data):
    """
    Validar datos de un visitante
    """
    errors = []
    
    # Nombre
    if 'name' in data:
        if len(data['name']) < 3:
            errors.append("El nombre debe tener al menos 3 caracteres")
    
    # Email
    if 'email' in data:
        if data['email'] and not validate_email(data['email']):
            errors.append("Formato de email inválido")
    
    # Teléfono
    if 'phone' in data and data['phone']:
        phone_regex = r'^\+?[0-9]{8,15}$'
        if not re.match(phone_regex, data['phone']):
            errors.append("Formato de teléfono inválido")
    
    return errors

def validate_user_data(data):
    """
    Validar datos de usuario
    """
    errors = []
    
    # Email
    if 'email' in data:
        if not validate_email(data['email']):
            errors.append("Formato de email inválido")
    
    # Contraseña
    if 'password' in data:
        if not validate_password(data['password']):
            errors.append("La contraseña debe tener al menos 8 caracteres, una letra mayúscula, una minúscula y un número")
    
    # Nombre
    if 'name' in data:
        if len(data['name']) < 3:
            errors.append("El nombre debe tener al menos 3 caracteres")
    
    # Rol
    if 'role' in data:
        if data['role'] not in ['admin', 'staff', 'guest']:
            errors.append("Rol inválido. Debe ser 'admin', 'staff' o 'guest'")
    
    return errors

def configure_validators(app):
    """
    Configura validadores globales para la aplicación
    
    Args:
        app: Aplicación Flask
    """
    # Registro de funciones de validación para uso en toda la aplicación
    app.jinja_env.globals.update(
        validate_email=validate_email,
        validate_password=validate_password
    )
    
    app.logger.info("Validadores configurados correctamente")
    
    return app 