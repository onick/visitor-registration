"""
Modelo para eventos
"""
from datetime import datetime
from .database import db

class Event(db.Model):
    """
    Modelo de evento cultural
    """
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    image_url = db.Column(db.String(500))
    # Campo type comentado para evitar errores con la base de datos PostgreSQL
    # type = db.Column(db.String(50), default="otro")  # Tipo de evento: cine, exposición, charla, etc.
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    visitors = db.relationship('VisitorCheckIn', backref='event', lazy=True)
    
    def __repr__(self):
        return f'<Event {self.title}>'
    
    @property
    def is_ongoing(self):
        """
        Verificar si el evento está en curso actualmente
        """
        now = datetime.utcnow()
        return self.start_date <= now <= self.end_date and self.is_active
