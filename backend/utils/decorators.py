"""
Decoradores para protección de rutas y autorización
"""
from functools import wraps
from flask import jsonify, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

def admin_required():
    """
    Decorador para proteger rutas solo para administradores
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            
            print(f"DEBUG - admin_required - User ID: {user_id}")
            
            # Importar aquí para evitar importaciones circulares
            from models.user import User
            user = User.query.get(user_id)
            
            print(f"DEBUG - admin_required - User encontrado: {user is not None}")
            if user:
                print(f"DEBUG - admin_required - Rol del usuario: {user.role}")
            
            if not user or user.role != 'admin':
                print(f"DEBUG - admin_required - Acceso denegado")
                return jsonify(error="Admin privilege required"), 403
            
            print(f"DEBUG - admin_required - Acceso permitido")
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
            user_id = get_jwt_identity()
            
            print(f"DEBUG - role_required - User ID: {user_id}")
            print(f"DEBUG - role_required - Roles permitidos: {allowed_roles}")
            
            # Importar aquí para evitar importaciones circulares
            from models.user import User
            user = User.query.get(user_id)
            
            print(f"DEBUG - role_required - User encontrado: {user is not None}")
            if user:
                print(f"DEBUG - role_required - Rol del usuario: {user.role}")
            
            if not user or user.role not in allowed_roles:
                print(f"DEBUG - role_required - Acceso denegado")
                return jsonify(error="Insufficient privileges"), 403
            
            print(f"DEBUG - role_required - Acceso permitido")
            return fn(*args, **kwargs)
        return decorator
    return wrapper 