"""
Servicio para la gestión de visitantes
"""
from models.visitor import Visitor, VisitorCheckIn
from models.database import db
from datetime import datetime

class VisitorService:
    """
    Clase de servicio para operaciones relacionadas con visitantes
    """
    
    @staticmethod
    def create_visitor(visitor_data):
        """
        Crear un nuevo visitante o actualizar uno existente si el correo coincide
        """
        # Si se proporciona un correo, verificar si ya existe
        if visitor_data.get('email'):
            existing_visitor = Visitor.query.filter_by(email=visitor_data.get('email')).first()
            if existing_visitor:
                # Actualizar datos del visitante existente
                existing_visitor.name = visitor_data.get('name', existing_visitor.name)
                existing_visitor.phone = visitor_data.get('phone', existing_visitor.phone)
                db.session.commit()
                return existing_visitor
        
        # Crear nuevo visitante
        visitor = Visitor(
            name=visitor_data.get('name'),
            email=visitor_data.get('email'),
            phone=visitor_data.get('phone')
        )
        
        db.session.add(visitor)
        db.session.commit()
        return visitor
    
    @staticmethod
    def get_visitor_by_id(visitor_id):
        """
        Obtener un visitante por su ID
        """
        return Visitor.query.get(visitor_id)
    
    @staticmethod
    def register_check_in(check_in_data):
        """
        Registrar la asistencia de un visitante a un evento
        """
        # Verificar si el visitante ya se registró en este evento
        existing_check_in = VisitorCheckIn.query.filter_by(
            visitor_id=check_in_data.get('visitor_id'),
            event_id=check_in_data.get('event_id')
        ).first()
        
        # Si ya existe un registro, no crear uno nuevo
        if existing_check_in:
            return existing_check_in
        
        # Crear nuevo registro de asistencia
        check_in = VisitorCheckIn(
            visitor_id=check_in_data.get('visitor_id'),
            event_id=check_in_data.get('event_id'),
            kiosk_id=check_in_data.get('kiosk_id')
        )
        
        db.session.add(check_in)
        db.session.commit()
        return check_in
    
    @staticmethod
    def get_visitors_by_event(event_id):
        """
        Obtener todos los visitantes registrados en un evento específico
        """
        check_ins = VisitorCheckIn.query.filter_by(event_id=event_id).all()
        visitors = []
        
        for check_in in check_ins:
            visitor = check_in.visitor
            # Agregar información de check-in al visitante
            visitor_info = {
                'id': visitor.id,
                'name': visitor.name,
                'email': visitor.email,
                'phone': visitor.phone,
                'check_in_time': check_in.check_in_time
            }
            visitors.append(visitor_info)
        
        return visitors
    
    @staticmethod
    def get_check_in_statistics(event_id=None, start_date=None, end_date=None):
        """
        Obtener estadísticas de registro de visitantes
        """
        query = db.session.query(
            db.func.count(VisitorCheckIn.id).label('total_check_ins')
        )
        
        if event_id:
            query = query.filter(VisitorCheckIn.event_id == event_id)
        
        if start_date:
            query = query.filter(VisitorCheckIn.check_in_time >= start_date)
        
        if end_date:
            query = query.filter(VisitorCheckIn.check_in_time <= end_date)
        
        result = query.first()
        return {'total_check_ins': result.total_check_ins if result else 0}
