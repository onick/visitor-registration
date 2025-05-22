"""
Modelo para visitantes del sistema
"""
from datetime import datetime
import secrets
import string
import json
from .database import db

class Visitor(db.Model):
    """
    Modelo para visitantes
    """
    __tablename__ = 'visitors'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    registration_code = db.Column(db.String(10), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Campos adicionales
    dob = db.Column(db.Date, nullable=True)  # Fecha de nacimiento
    address = db.Column(db.String(200), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    postal_code = db.Column(db.String(20), nullable=True)
    occupation = db.Column(db.String(100), nullable=True)
    company = db.Column(db.String(100), nullable=True)
    interests = db.Column(db.String(500), nullable=True)  # Intereses separados por comas
    
    # Relaciones
    events = db.relationship('Event', secondary='event_visitors', back_populates='visitors')
    registrations = db.relationship('EventVisitor', back_populates='visitor')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.registration_code:
            self.registration_code = self.generate_unique_code()
    
    @staticmethod
    def generate_unique_code():
        """Genera un código único de 6 caracteres alfanuméricos"""
        characters = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(secrets.choice(characters) for _ in range(6))
            # Verificar que el código no exista
            if not Visitor.query.filter_by(registration_code=code).first():
                return code
    
    def __repr__(self):
        return f'<Visitor {self.name}>'
        
    def to_dict(self):
        """
        Convierte el visitante a un diccionario
        """
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'registration_code': self.registration_code,
            'created_at': self.created_at.isoformat(),
            'dob': self.dob.isoformat() if self.dob else None,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'postal_code': self.postal_code,
            'occupation': self.occupation,
            'company': self.company,
            'interests': self.interests.split(',') if self.interests else []
        }

class EventVisitor(db.Model):
    """
    Modelo para la relación entre visitantes y eventos
    """
    __tablename__ = 'event_visitors'
    
    id = db.Column(db.Integer, primary_key=True)
    visitor_id = db.Column(db.Integer, db.ForeignKey('visitors.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    registration_code = db.Column(db.String(10), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    check_in_time = db.Column(db.DateTime, nullable=True)
    registered_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    checked_in_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    status = db.Column(db.String(20), default='REGISTERED')  # REGISTERED, CHECKED_IN, NO_SHOW, CANCELED
    notes = db.Column(db.Text, nullable=True)
    
    # Relaciones
    visitor = db.relationship('Visitor', back_populates='registrations')
    event = db.relationship('Event', back_populates='registrations')
    registered_by_user = db.relationship('User', foreign_keys=[registered_by])
    checked_in_by_user = db.relationship('User', foreign_keys=[checked_in_by])
    
    def __repr__(self):
        return f'<EventVisitor {self.visitor_id} - {self.event_id}>'
        
    def to_dict(self):
        """
        Convierte el registro a un diccionario
        """
        return {
            'id': self.id,
            'visitor_id': self.visitor_id,
            'event_id': self.event_id,
            'registration_code': self.registration_code,
            'registration_date': self.registration_date.isoformat(),
            'check_in_time': self.check_in_time.isoformat() if self.check_in_time else None,
            'registered_by': self.registered_by,
            'checked_in_by': self.checked_in_by,
            'status': self.status,
            'notes': self.notes,
            'visitor': self.visitor.to_dict() if self.visitor else None,
            'event': self.event.to_dict() if self.event else None
        }
        
    @property
    def is_checked_in(self):
        """
        Indica si el visitante ha hecho check-in
        """
        return self.status == 'CHECKED_IN'
        
    @property
    def is_registered(self):
        """
        Indica si el visitante está registrado
        """
        return self.status == 'REGISTERED'
        
    @property
    def is_no_show(self):
        """
        Indica si el visitante no se presentó
        """
        return self.status == 'NO_SHOW'
        
    @property
    def is_canceled(self):
        """
        Indica si el registro fue cancelado
        """
        return self.status == 'CANCELED'
        
    def check_in(self, checked_in_by=None):
        """
        Registra el check-in del visitante
        """
        self.check_in_time = datetime.utcnow()
        self.status = 'CHECKED_IN'
        self.checked_in_by = checked_in_by
        return True
        
    def mark_as_no_show(self):
        """
        Marca al visitante como no presentado
        """
        self.status = 'NO_SHOW'
        return True
        
    def cancel_registration(self, note=None):
        """
        Cancela el registro del visitante
        """
        self.status = 'CANCELED'
        if note:
            self.notes = note if not self.notes else f"{self.notes}\n{note}"
        return True

class VisitorCheckIn(db.Model):
    """
    Modelo para registrar asistencia de visitantes a eventos
    """
    __tablename__ = 'visitor_check_ins'
    
    id = db.Column(db.Integer, primary_key=True)
    visitor_id = db.Column(db.Integer, db.ForeignKey('visitors.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    kiosk_id = db.Column(db.Integer, db.ForeignKey('kiosks.id'), nullable=False)
    check_in_time = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<VisitorCheckIn visitor_id={self.visitor_id} event_id={self.event_id}>'

