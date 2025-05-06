"""
Endpoints para la gestión de kioscos
"""
from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required
from models.kiosk import Kiosk, KioskConfig
from models.event import Event
from models.database import db
from datetime import datetime
from utils.validators import validate_required_fields
from utils.decorators import role_required

kiosks_namespace = Namespace('kiosks', description='Operaciones relacionadas con kioscos')

# Modelos para la documentación de la API
kiosk_model = kiosks_namespace.model('Kiosk', {
    'id': fields.Integer(readonly=True, description='Identificador único del kiosco'),
    'name': fields.String(required=True, description='Nombre del kiosco'),
    'location': fields.String(required=True, description='Ubicación física del kiosco'),
    'is_active': fields.Boolean(default=True, description='Estado del kiosco'),
    'last_heartbeat': fields.DateTime(description='Último reporte de actividad'),
    'created_at': fields.DateTime(readonly=True, description='Fecha de creación')
})

kiosk_config_model = kiosks_namespace.model('KioskConfig', {
    'kiosk_id': fields.Integer(required=True, description='ID del kiosco'),
    'language': fields.String(default='es', description='Idioma predeterminado'),
    'idle_timeout': fields.Integer(default=60, description='Tiempo de inactividad en segundos'),
    'event_filter': fields.String(description='Filtro de eventos para este kiosco'),
    'custom_message': fields.String(description='Mensaje personalizado de bienvenida'),
    'logo_url': fields.String(description='URL del logo personalizado')
})

kiosk_status_model = kiosks_namespace.model('KioskStatus', {
    'id': fields.Integer(description='ID del kiosco'),
    'name': fields.String(description='Nombre del kiosco'),
    'location': fields.String(description='Ubicación del kiosco'),
    'is_active': fields.Boolean(description='Estado del kiosco'),
    'is_online': fields.Boolean(description='Estado de conexión'),
    'last_heartbeat': fields.DateTime(description='Último reporte de actividad')
})

@kiosks_namespace.route('/')
class KioskList(Resource):
    """
    Operaciones para lista de kioscos
    """
    @kiosks_namespace.doc('list_kiosks', security='apikey')
    @kiosks_namespace.marshal_list_with(kiosk_model)
    @jwt_required()
    @role_required(['admin', 'staff'])
    def get(self):
        """
        Obtener lista de kioscos
        """
        # Implementación para obtener kioscos desde la base de datos
        kiosks = Kiosk.query.all()
        return kiosks
    
    @kiosks_namespace.doc('create_kiosk', security='apikey')
    @kiosks_namespace.expect(kiosk_model)
    @kiosks_namespace.marshal_with(kiosk_model, code=201)
    @jwt_required()
    @role_required(['admin'])
    @validate_required_fields(['name', 'location'])
    def post(self):
        """
        Registrar un nuevo kiosco
        """
        # Implementación para crear un kiosco
        data = request.json
        
        # Validar datos básicos
        if len(data['name']) < 3:
            return {'error': 'El nombre debe tener al menos 3 caracteres'}, 400
            
        if len(data['location']) < 3:
            return {'error': 'La ubicación debe tener al menos 3 caracteres'}, 400
        
        new_kiosk = Kiosk(
            name=data['name'],
            location=data['location'],
            is_active=data.get('is_active', True)
        )
        
        db.session.add(new_kiosk)
        db.session.commit()
        
        # Crear configuración por defecto
        config = KioskConfig(
            kiosk_id=new_kiosk.id,
            language='es',
            idle_timeout=60
        )
        
        db.session.add(config)
        db.session.commit()
        
        return new_kiosk, 201

@kiosks_namespace.route('/<int:id>')
@kiosks_namespace.param('id', 'Identificador del kiosco')
class KioskResource(Resource):
    """
    Operaciones para kioscos individuales
    """
    @kiosks_namespace.doc('get_kiosk')
    @kiosks_namespace.marshal_with(kiosk_model)
    def get(self, id):
        """
        Obtener información de un kiosco por su ID
        """
        # Implementación para obtener un kiosco por ID
        kiosk = Kiosk.query.get_or_404(id)
        return kiosk
    
    @kiosks_namespace.doc('update_kiosk', security='apikey')
    @kiosks_namespace.expect(kiosk_model)
    @kiosks_namespace.marshal_with(kiosk_model)
    @jwt_required()
    @role_required(['admin'])
    def put(self, id):
        """
        Actualizar información de un kiosco
        """
        # Implementación para actualizar un kiosco
        kiosk = Kiosk.query.get_or_404(id)
        data = request.json
        
        # Validar datos básicos si se proporcionan
        if 'name' in data and len(data['name']) < 3:
            return {'error': 'El nombre debe tener al menos 3 caracteres'}, 400
            
        if 'location' in data and len(data['location']) < 3:
            return {'error': 'La ubicación debe tener al menos 3 caracteres'}, 400
        
        if 'name' in data:
            kiosk.name = data['name']
            
        if 'location' in data:
            kiosk.location = data['location']
            
        if 'is_active' in data:
            kiosk.is_active = data['is_active']
        
        db.session.commit()
        return kiosk
    
    @kiosks_namespace.doc('delete_kiosk', security='apikey')
    @jwt_required()
    @role_required(['admin'])
    def delete(self, id):
        """
        Eliminar un kiosco
        """
        kiosk = Kiosk.query.get_or_404(id)
        
        # Eliminar configuración asociada
        config = KioskConfig.query.filter_by(kiosk_id=id).first()
        if config:
            db.session.delete(config)
            
        db.session.delete(kiosk)
        db.session.commit()
        
        return '', 204

@kiosks_namespace.route('/<int:id>/config')
@kiosks_namespace.param('id', 'Identificador del kiosco')
class KioskConfigResource(Resource):
    """
    Operaciones para configuración de kioscos
    """
    @kiosks_namespace.doc('get_kiosk_config')
    @kiosks_namespace.marshal_with(kiosk_config_model)
    def get(self, id):
        """
        Obtener configuración de un kiosco
        """
        # Implementación para obtener configuración de kiosco
        # Primero verificamos que el kiosco exista
        Kiosk.query.get_or_404(id)
        
        config = KioskConfig.query.filter_by(kiosk_id=id).first()
        if not config:
            # Si no existe configuración, creamos una por defecto
            config = KioskConfig(
                kiosk_id=id,
                language='es',
                idle_timeout=60
            )
            db.session.add(config)
            db.session.commit()
            
        return config
    
    @kiosks_namespace.doc('update_kiosk_config', security='apikey')
    @kiosks_namespace.expect(kiosk_config_model)
    @kiosks_namespace.marshal_with(kiosk_config_model)
    @jwt_required()
    @role_required(['admin', 'staff'])
    def put(self, id):
        """
        Actualizar configuración de un kiosco
        """
        # Implementación para actualizar configuración de kiosco
        # Primero verificamos que el kiosco exista
        Kiosk.query.get_or_404(id)
        
        config = KioskConfig.query.filter_by(kiosk_id=id).first()
        if not config:
            # Si no existe configuración, creamos una nueva
            config = KioskConfig(kiosk_id=id)
            db.session.add(config)
            
        data = request.json
        
        # Validación básica
        if 'idle_timeout' in data and data['idle_timeout'] < 10:
            return {'error': 'El tiempo de inactividad debe ser al menos 10 segundos'}, 400
        
        if 'language' in data:
            config.language = data['language']
            
        if 'idle_timeout' in data:
            config.idle_timeout = data['idle_timeout']
            
        if 'event_filter' in data:
            config.event_filter = data['event_filter']
            
        if 'custom_message' in data:
            config.custom_message = data['custom_message']
            
        if 'logo_url' in data:
            config.logo_url = data['logo_url']
        
        db.session.commit()
        return config

@kiosks_namespace.route('/<int:id>/heartbeat')
@kiosks_namespace.param('id', 'Identificador del kiosco')
class KioskHeartbeat(Resource):
    """
    Endpoint para reportar actividad de kiosco
    """
    @kiosks_namespace.doc('kiosk_heartbeat')
    def post(self, id):
        """
        Reportar que el kiosco está activo
        """
        # Implementación para actualizar último heartbeat del kiosco
        kiosk = Kiosk.query.get_or_404(id)
        kiosk.last_heartbeat = datetime.utcnow()
        db.session.commit()
        
        return {'status': 'ok', 'is_active': kiosk.is_active}, 200

@kiosks_namespace.route('/<int:id>/events')
@kiosks_namespace.param('id', 'Identificador del kiosco')
class KioskEvents(Resource):
    """
    Endpoint para obtener eventos relevantes para un kiosco
    """
    @kiosks_namespace.doc('kiosk_events')
    def get(self, id):
        """
        Obtener lista de eventos activos relevantes para este kiosco
        """
        # Implementación para filtrar eventos por kiosco
        kiosk = Kiosk.query.get_or_404(id)
        
        # Verificar si el kiosco está activo
        if not kiosk.is_active:
            return {'error': 'El kiosco no está activo'}, 400
        
        # Obtenemos la configuración del kiosco para ver si hay filtros de eventos
        config = KioskConfig.query.filter_by(kiosk_id=id).first()
        
        # Base query para eventos activos
        query = Event.query.filter_by(is_active=True)
        
        # Si hay filtro de eventos en la configuración, aplicarlo
        if config and config.event_filter:
            # Esto es un ejemplo simple, podría ser más complejo dependiendo
            # de cómo se defina el filtro en event_filter
            event_ids = [int(id) for id in config.event_filter.split(',') if id.strip().isdigit()]
            if event_ids:
                query = query.filter(Event.id.in_(event_ids))
        
        # Filtrar solo eventos que no hayan terminado
        now = datetime.utcnow()
        query = query.filter(Event.end_date > now)
        
        events = query.all()
        
        # Transformamos los objetos Event a diccionarios para el retorno
        result = [{
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'start_date': event.start_date.isoformat(),
            'end_date': event.end_date.isoformat(),
            'location': event.location,
            'image_url': event.image_url,
            'is_ongoing': event.is_ongoing
        } for event in events]
        
        return result, 200

@kiosks_namespace.route('/status')
class KioskStatusList(Resource):
    """
    Endpoint para obtener estado de todos los kioscos
    """
    @kiosks_namespace.doc('kiosk_status_list', security='apikey')
    @kiosks_namespace.marshal_list_with(kiosk_status_model)
    @jwt_required()
    @role_required(['admin', 'staff'])
    def get(self):
        """
        Obtener estado de todos los kioscos
        """
        kiosks = Kiosk.query.all()
        result = []
        
        for kiosk in kiosks:
            result.append({
                'id': kiosk.id,
                'name': kiosk.name,
                'location': kiosk.location,
                'is_active': kiosk.is_active,
                'is_online': kiosk.is_online,
                'last_heartbeat': kiosk.last_heartbeat
            })
        
        return result
