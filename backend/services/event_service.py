"""
Servicio para la gestión de eventos
"""
from models.event import Event
from models.database import db
from datetime import datetime
from sqlalchemy import and_

class EventService:
    """
    Clase de servicio para operaciones relacionadas con eventos
    """
    
    @staticmethod
    def get_all_events(active_only=False, date=None):
        """
        Obtener todos los eventos, con filtros opcionales
        """
        query = Event.query
        
        if active_only:
            query = query.filter(Event.is_active == True)
        
        if date:
            try:
                filter_date = datetime.strptime(date, '%Y-%m-%d')
                # Filtrar eventos que ocurran en la fecha especificada
                query = query.filter(
                    and_(
                        Event.start_date <= datetime.combine(filter_date, datetime.max.time()),
                        Event.end_date >= datetime.combine(filter_date, datetime.min.time())
                    )
                )
            except ValueError:
                # Si el formato de fecha es incorrecto, ignorar este filtro
                pass
        
        return query.order_by(Event.start_date).all()
    
    @staticmethod
    def get_event_by_id(event_id):
        """
        Obtener un evento por su ID
        """
        return Event.query.get(event_id)
    
    @staticmethod
    def create_event(event_data):
        """
        Crear un nuevo evento
        """
        event = Event(
            title=event_data.get('title'),
            description=event_data.get('description'),
            start_date=event_data.get('start_date'),
            end_date=event_data.get('end_date'),
            location=event_data.get('location'),
            image_url=event_data.get('image_url'),
            is_active=event_data.get('is_active', True)
        )
        
        db.session.add(event)
        db.session.commit()
        return event
    
    @staticmethod
    def update_event(event_id, event_data):
        """
        Actualizar un evento existente
        """
        event = Event.query.get(event_id)
        
        if not event:
            return None
        
        # Actualizar solo los campos proporcionados
        if 'title' in event_data:
            event.title = event_data['title']
        if 'description' in event_data:
            event.description = event_data['description']
        if 'start_date' in event_data:
            event.start_date = event_data['start_date']
        if 'end_date' in event_data:
            event.end_date = event_data['end_date']
        if 'location' in event_data:
            event.location = event_data['location']
        if 'image_url' in event_data:
            event.image_url = event_data['image_url']
        if 'is_active' in event_data:
            event.is_active = event_data['is_active']
        
        db.session.commit()
        return event
    
    @staticmethod
    def delete_event(event_id):
        """
        Eliminar un evento
        """
        event = Event.query.get(event_id)
        
        if not event:
            return False
        
        db.session.delete(event)
        db.session.commit()
        return True
    
    @staticmethod
    def get_active_events_for_kiosk(kiosk_id):
        """
        Obtener eventos activos relevantes para un kiosco específico
        """
        from models.kiosk import KioskConfig
        
        # Obtener configuración del kiosco
        config = KioskConfig.query.filter_by(kiosk_id=kiosk_id).first()
        
        # Consulta base: eventos activos que están en curso o próximos
        now = datetime.utcnow()
        query = Event.query.filter(
            Event.is_active == True,
            Event.end_date >= now
        )
        
        # Si el kiosco tiene un filtro de eventos, aplicarlo
        if config and config.event_filter:
            # Implementar lógica de filtrado según event_filter
            # Por simplicidad, asumimos que event_filter podría ser una ubicación
            if 'location=' in config.event_filter:
                location = config.event_filter.split('=')[1]
                query = query.filter(Event.location == location)
        
        # Ordenar por fecha de inicio (primero los eventos en curso)
        return query.order_by(Event.start_date).all()
