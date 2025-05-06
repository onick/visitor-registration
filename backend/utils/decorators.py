"""
Decoradores para protección de rutas y autorización
"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def admin_required():
    """
    Decorador para proteger rutas solo para administradores
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            
            if claims.get('role') != 'admin':
                return jsonify(error="Admin privilege required"), 403
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def role_required(allowed_roles):
    """
    Decorador para proteger rutas basado en roles
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            
            if claims.get('role') not in allowed_roles:
                return jsonify(error="Insufficient privileges"), 403
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper 