"""
Endpoints para la gestión de notificaciones
"""
from flask_restx import Namespace, Resource, fields
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.notification import Notification
from models.user import User
from models.database import db
from datetime import datetime
from utils.decorators import role_required
from sqlalchemy import desc

notifications_namespace = Namespace('notifications', description='Operaciones relacionadas con notificaciones')

# Modelos para la documentación de la API
notification_model = notifications_namespace.model('Notification', {
    'id': fields.Integer(readonly=True, description='Identificador único de la notificación'),
    'title': fields.String(required=True, description='Título de la notificación'),
    'message': fields.String(required=True, description='Mensaje de la notificación'),
    'type': fields.String(required=True, description='Tipo de notificación (info, warning, error, success)'),
    'for_role': fields.String(description='Rol específico al que va dirigida (null = todos)'),
    'for_user_id': fields.Integer(description='ID del usuario específico (null = todos)'),
    'created_at': fields.DateTime(readonly=True, description='Fecha de creación'),
    'is_read': fields.Boolean(description='Indica si la notificación ha sido leída'),
    'read_at': fields.DateTime(description='Fecha de lectura')
})

# Modelo para la creación de notificaciones
notification_create_model = notifications_namespace.model('NotificationCreate', {
    'title': fields.String(required=True, description='Título de la notificación'),
    'message': fields.String(required=True, description='Mensaje de la notificación'),
    'type': fields.String(required=True, description='Tipo de notificación (info, warning, error, success)'),
    'for_role': fields.String(description='Rol específico al que va dirigida (null = todos)'),
    'for_user_id': fields.Integer(description='ID del usuario específico (null = todos)')
})

@notifications_namespace.route('/')
class NotificationList(Resource):
    """
    Operaciones para lista de notificaciones
    """
    @notifications_namespace.doc('list_notifications', security='apikey')
    @notifications_namespace.marshal_list_with(notification_model)
    @jwt_required()
    def get(self):
        """
        Obtener notificaciones para el usuario actual
        """
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return [], 200
        
        # Obtener notificaciones para este usuario (específicas o para su rol)
        notifications = Notification.query.filter(
            ((Notification.for_user_id == current_user.id) | 
             (Notification.for_user_id.is_(None))) &
            ((Notification.for_role == current_user.role) | 
             (Notification.for_role.is_(None)))
        ).order_by(desc(Notification.created_at)).all()
        
        return notifications
    
    @notifications_namespace.doc('create_notification', security='apikey')
    @notifications_namespace.expect(notification_create_model)
    @notifications_namespace.marshal_with(notification_model, code=201)
    @jwt_required()
    @role_required(['admin'])
    def post(self):
        """
        Crear una nueva notificación
        """
        data = request.json
        
        # Validar el tipo de notificación
        valid_types = ['info', 'warning', 'error', 'success']
        if data.get('type') not in valid_types:
            return {'error': f'Tipo de notificación inválido. Use: {", ".join(valid_types)}'}, 400
        
        # Validar campos requeridos
        if not data.get('title') or not data.get('message'):
            return {'error': 'Título y mensaje son requeridos'}, 400
        
        # Validar usuario si se especifica
        if data.get('for_user_id'):
            user = User.query.get(data.get('for_user_id'))
            if not user:
                return {'error': 'Usuario no encontrado'}, 404
        
        # Validar rol si se especifica
        if data.get('for_role') and data.get('for_role') not in ['admin', 'staff']:
            return {'error': 'Rol inválido. Use: admin, staff'}, 400
        
        # Crear la notificación
        notification = Notification(
            title=data.get('title'),
            message=data.get('message'),
            type=data.get('type'),
            for_role=data.get('for_role'),
            for_user_id=data.get('for_user_id')
        )
        
        db.session.add(notification)
        db.session.commit()
        
        return notification, 201

@notifications_namespace.route('/<int:id>')
@notifications_namespace.param('id', 'Identificador de la notificación')
class NotificationResource(Resource):
    """
    Operaciones para notificaciones individuales
    """
    @notifications_namespace.doc('get_notification', security='apikey')
    @notifications_namespace.marshal_with(notification_model)
    @jwt_required()
    def get(self, id):
        """
        Obtener una notificación por su ID
        """
        current_user_id = get_jwt_identity()
        notification = Notification.query.get_or_404(id)
        
        # Verificar que la notificación sea para este usuario
        if notification.for_user_id is not None and notification.for_user_id != current_user_id:
            return {'error': 'No autorizado'}, 403
        
        # Si la notificación es para un rol específico, verificar que el usuario tenga ese rol
        if notification.for_role is not None:
            current_user = User.query.get(current_user_id)
            if current_user.role != notification.for_role:
                return {'error': 'No autorizado'}, 403
        
        return notification
    
    @notifications_namespace.doc('mark_read', security='apikey')
    @notifications_namespace.marshal_with(notification_model)
    @jwt_required()
    def put(self, id):
        """
        Marcar una notificación como leída
        """
        current_user_id = get_jwt_identity()
        notification = Notification.query.get_or_404(id)
        
        # Verificar que la notificación sea para este usuario
        if notification.for_user_id is not None and notification.for_user_id != current_user_id:
            return {'error': 'No autorizado'}, 403
        
        # Si la notificación es para un rol específico, verificar que el usuario tenga ese rol
        if notification.for_role is not None:
            current_user = User.query.get(current_user_id)
            if current_user.role != notification.for_role:
                return {'error': 'No autorizado'}, 403
        
        # Marcar como leída
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        db.session.commit()
        
        return notification
    
    @notifications_namespace.doc('delete_notification', security='apikey')
    @jwt_required()
    @role_required(['admin'])
    def delete(self, id):
        """
        Eliminar una notificación
        """
        notification = Notification.query.get_or_404(id)
        
        db.session.delete(notification)
        db.session.commit()
        
        return '', 204

@notifications_namespace.route('/mark-all-read')
class MarkAllRead(Resource):
    """
    Operación para marcar todas las notificaciones como leídas
    """
    @notifications_namespace.doc('mark_all_read', security='apikey')
    @jwt_required()
    def post(self):
        """
        Marcar todas las notificaciones del usuario como leídas
        """
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return {'message': 'No hay notificaciones para marcar'}, 200
        
        # Obtener notificaciones sin leer para este usuario
        notifications = Notification.query.filter(
            ((Notification.for_user_id == current_user.id) | 
             (Notification.for_user_id.is_(None))) &
            ((Notification.for_role == current_user.role) | 
             (Notification.for_role.is_(None))) &
            (Notification.is_read == False)
        ).all()
        
        # Marcar todas como leídas
        now = datetime.utcnow()
        for notification in notifications:
            notification.is_read = True
            notification.read_at = now
        
        db.session.commit()
        
        return {'message': f'Se marcaron {len(notifications)} notificaciones como leídas'}, 200

@notifications_namespace.route('/unread-count')
class UnreadCount(Resource):
    """
    Operación para obtener cantidad de notificaciones sin leer
    """
    @notifications_namespace.doc('unread_count', security='apikey')
    @jwt_required()
    def get(self):
        """
        Obtener cantidad de notificaciones sin leer para el usuario actual
        """
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return {'count': 0}, 200
        
        # Contar notificaciones sin leer para este usuario
        count = Notification.query.filter(
            ((Notification.for_user_id == current_user.id) | 
             (Notification.for_user_id.is_(None))) &
            ((Notification.for_role == current_user.role) | 
             (Notification.for_role.is_(None))) &
            (Notification.is_read == False)
        ).count()
        
        return {'count': count}, 200 