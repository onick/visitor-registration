"""
Decoradores para protección de rutas y autorización
"""
from functools import wraps
from flask import jsonify, current_app, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
import json
import time
from flask_limiter import Limiter

# Configuración global para el rate limiter
limiter = Limiter(
    key_func=lambda: request.remote_addr,  # Identificar por IP
    default_limits=["200 per day", "50 per hour"]
)

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

def permission_required(permission_name):
    """
    Decorador para proteger rutas basado en permisos específicos
    
    Args:
        permission_name (str): Nombre del permiso requerido
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            
            # Importar aquí para evitar importaciones circulares
            from models.user import User
            user = User.query.get(user_id)
            
            if not user:
                return jsonify(error="User not found"), 404
                
            if not user.has_permission(permission_name):
                return jsonify(error=f"Required permission: {permission_name}"), 403
            
            # Registrar acceso para auditoría si es necesario
            _log_access(user, permission_name, request)
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def permissions_required(permission_names):
    """
    Decorador para proteger rutas basado en múltiples permisos específicos
    
    Args:
        permission_names (list): Lista de nombres de permisos requeridos
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            
            # Importar aquí para evitar importaciones circulares
            from models.user import User
            user = User.query.get(user_id)
            
            if not user:
                return jsonify(error="User not found"), 404
                
            if not user.has_permissions(permission_names):
                return jsonify(error=f"Required permissions: {', '.join(permission_names)}"), 403
            
            # Registrar acceso para auditoría
            for permission in permission_names:
                _log_access(user, permission, request)
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def _log_access(user, permission, request):
    """
    Registra acceso para auditoría
    
    Args:
        user (User): Usuario que accede
        permission (str): Permiso utilizado
        request (Request): Objeto de solicitud Flask
    """
    try:
        from models.permission import AuditLog
        from models.database import db
        
        # Extraer información relevante de la solicitud
        entity_type = None
        entity_id = None
        
        # Intentar determinar el tipo de entidad y su ID de la ruta
        path_parts = request.path.strip('/').split('/')
        if len(path_parts) >= 2:
            potential_entity_types = ['events', 'visitors', 'users', 'kiosks']
            for i, part in enumerate(path_parts):
                if part in potential_entity_types and i + 1 < len(path_parts):
                    try:
                        entity_id = int(path_parts[i + 1])
                        entity_type = part[:-1]  # Quitar la 's' final (events -> event)
                        break
                    except (ValueError, IndexError):
                        pass
        
        # Crear registro de auditoría
        audit_log = AuditLog(
            user_id=user.id,
            action=f"ACCESS:{permission}",
            entity_type=entity_type or request.endpoint,
            entity_id=entity_id,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            details=json.dumps({
                'method': request.method,
                'path': request.path,
                'args': dict(request.args),
            })
        )
        
        db.session.add(audit_log)
        db.session.commit()
    except Exception as e:
        # No interrumpir el flujo principal si falla el registro de auditoría
        current_app.logger.error(f"Error al registrar auditoría: {str(e)}")

def log_action(action, entity_type, entity_id=None, details=None):
    """
    Decorador para registrar acciones después de que se completan exitosamente
    
    Args:
        action (str): Acción realizada (CREATE, UPDATE, DELETE, etc.)
        entity_type (str): Tipo de entidad (event, visitor, user, etc.)
        entity_id (int, optional): ID de la entidad, puede ser None si no aplica
        details (dict, optional): Detalles adicionales de la acción
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            # Ejecutar la función original
            result = fn(*args, **kwargs)
            
            # Solo registrar si la función se completó exitosamente
            try:
                verify_jwt_in_request()
                user_id = get_jwt_identity()
                
                from models.user import User
                from models.permission import AuditLog
                from models.database import db
                
                user = User.query.get(user_id)
                
                # Extraer el ID de la entidad de los argumentos o del resultado
                actual_entity_id = entity_id
                if actual_entity_id is None and isinstance(result, dict) and 'id' in result:
                    actual_entity_id = result['id']
                
                # Crear registro de auditoría
                audit_log = AuditLog(
                    user_id=user.id if user else None,
                    action=action,
                    entity_type=entity_type,
                    entity_id=actual_entity_id,
                    ip_address=request.remote_addr,
                    user_agent=request.user_agent.string if request else None,
                    details=json.dumps(details) if details else None
                )
                
                db.session.add(audit_log)
                db.session.commit()
            except Exception as e:
                # No interrumpir el flujo principal si falla el registro de auditoría
                current_app.logger.error(f"Error al registrar acción: {str(e)}")
            
            return result
        return decorator
    return wrapper 