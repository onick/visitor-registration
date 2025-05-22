"""
Configuración y utilidades para el sistema de caché
"""
from flask_caching import Cache
from functools import wraps
import json
from flask import request, current_app

# Instancia global de caché
cache = Cache()

def init_cache(app):
    """
    Inicializa el sistema de caché con la aplicación Flask
    
    Args:
        app: Aplicación Flask
    """
    cache.init_app(app)
    return cache

def cached(timeout=300, key_prefix='view/%s', unless=None):
    """
    Decorador para cachear respuestas de vistas
    
    Args:
        timeout (int): Tiempo de expiración en segundos
        key_prefix (str): Prefijo para la clave de caché
        unless (callable): Función que devuelve True si no se debe cachear
        
    Returns:
        decorator: Decorador para cachear respuestas
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # No cachear si se especifica en la URL
            if request.args.get('no_cache'):
                return f(*args, **kwargs)
                
            # Generar clave única para esta solicitud
            cache_key = key_prefix % request.path
            
            # Agregar parámetros de consulta a la clave
            if request.args:
                cache_key += '?' + '&'.join([f"{k}={v}" for k, v in sorted(request.args.items()) if k != 'no_cache'])
            
            # Verificar si hay resultado en caché
            rv = cache.get(cache_key)
            if rv is not None:
                # Deserializar si es necesario
                if isinstance(rv, str):
                    try:
                        rv = json.loads(rv)
                    except:
                        pass
                return rv
                
            # Ejecutar función original
            rv = f(*args, **kwargs)
            
            # Cachear resultado si es necesario
            if unless and unless():
                return rv
                
            # Serializar si es necesario
            cache_value = rv
            if not isinstance(rv, (str, bytes, int, float, bool)):
                try:
                    cache_value = json.dumps(rv)
                except:
                    current_app.logger.warning(f"No se pudo serializar respuesta para caché: {rv}")
            
            # Guardar en caché
            cache.set(cache_key, cache_value, timeout=timeout)
            return rv
            
        return decorated_function
    return decorator

def cache_clear_pattern(pattern):
    """
    Limpia todas las entradas de caché que coincidan con un patrón
    
    Args:
        pattern (str): Patrón para coincidencia de claves
        
    Returns:
        int: Número de entradas eliminadas
    """
    # Este método depende del backend de caché
    if hasattr(cache, 'delete_memoized'):
        cache.delete_memoized(pattern)
        return 1
    # Para SimpleCache, no hay forma de eliminar por patrón
    return 0

def cache_event_data(event_id, timeout=300):
    """
    Decorador específico para cachear datos de un evento
    
    Args:
        event_id (int): ID del evento
        timeout (int): Tiempo de expiración en segundos
        
    Returns:
        decorator: Decorador para cachear datos de evento
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = f"event_data/{event_id}"
            rv = cache.get(cache_key)
            if rv is not None:
                return rv
                
            rv = f(*args, **kwargs)
            cache.set(cache_key, rv, timeout=timeout)
            return rv
            
        return decorated_function
    return decorator

def invalidate_event_cache(event_id):
    """
    Invalida la caché para un evento específico
    
    Args:
        event_id (int): ID del evento
        
    Returns:
        bool: True si se invalidó correctamente, False en caso contrario
    """
    try:
        cache.delete(f"event_data/{event_id}")
        # También intentar invalidar patrones relacionados
        cache_clear_pattern(f"view/*/events/{event_id}*")
        return True
    except Exception as e:
        current_app.logger.error(f"Error al invalidar caché del evento {event_id}: {str(e)}")
        return False

def get_active_events_cached(timeout=300):
    """
    Obtiene eventos activos con caché
    
    Args:
        timeout (int): Tiempo de expiración en segundos
        
    Returns:
        list: Lista de eventos activos
    """
    from models.event import Event
    
    cache_key = "active_events"
    events = cache.get(cache_key)
    
    if events is not None:
        # Deserializar si es necesario
        if isinstance(events, str):
            try:
                events = json.loads(events)
            except:
                events = None
    
    if events is None:
        # Obtener eventos activos de la base de datos
        db_events = Event.query.filter_by(is_active=True).all()
        
        # Convertir a diccionarios
        events = [event.to_dict() for event in db_events]
        
        # Guardar en caché
        cache.set(cache_key, json.dumps(events), timeout=timeout)
    
    return events 