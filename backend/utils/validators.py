"""
Validadores para datos de entrada en la API
"""
import re
from datetime import datetime, timedelta
from flask import request, jsonify
from functools import wraps

def validate_email(email):
    """
    Validar formato de email
    """
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

def validate_password(password):
    """
    Validar complejidad de contraseña
    """
    # Al menos 8 caracteres, una letra mayúscula, una minúscula y un número
    if len(password) < 8:
        return False
    
    has_uppercase = any(c.isupper() for c in password)
    has_lowercase = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    
    return has_uppercase and has_lowercase and has_digit

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