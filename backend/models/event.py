"""
Modelo para eventos del sistema
"""
from datetime import datetime
from .database import db

class Event(db.Model):
    """
    Modelo para eventos
    """
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    capacity = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    event_type = db.Column(db.String(50), nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    
    # Relaciones
    visitors = db.relationship('Visitor', secondary='event_visitors', back_populates='events')
    registrations = db.relationship('EventVisitor', back_populates='event')
    created_by_user = db.relationship('User')
    
    def __repr__(self):
        return f'<Event {self.title}>'
    
    @property
    def is_upcoming(self):
        """
        Verifica si el evento aún no ha comenzado
        """
        return self.start_date > datetime.utcnow()
    
    @property
    def is_ongoing(self):
        """
        Verifica si el evento está en curso
        """
        now = datetime.utcnow()
        return self.start_date <= now and self.end_date >= now
    
    @property
    def is_past(self):
        """
        Verifica si el evento ya ha terminado
        """
        return self.end_date < datetime.utcnow()
    
    @property
    def registration_count(self):
        """
        Obtiene el número total de registros (excluyendo cancelados)
        """
        return len([r for r in self.registrations if r.status != 'CANCELED'])
    
    @property
    def checked_in_count(self):
        """
        Obtiene el número de visitantes que han hecho check-in
        """
        return len([r for r in self.registrations if r.status == 'CHECKED_IN'])
    
    @property
    def available_capacity(self):
        """
        Obtiene la capacidad disponible restante
        """
        if self.capacity <= 0:  # Capacidad ilimitada
            return float('inf')
        return max(0, self.capacity - self.registration_count)
    
    def to_dict(self):
        """
        Convierte el evento a un diccionario
        """
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'location': self.location,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'capacity': self.capacity,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'created_by': self.created_by,
            'event_type': self.event_type,
            'image_url': self.image_url,
            'registration_count': self.registration_count,
            'checked_in_count': self.checked_in_count,
            'available_capacity': self.available_capacity if self.available_capacity != float('inf') else None,
            'is_upcoming': self.is_upcoming,
            'is_ongoing': self.is_ongoing,
            'is_past': self.is_past
        }
