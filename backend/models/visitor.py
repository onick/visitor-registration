"""
Modelo para visitantes
"""
from datetime import datetime
from .database import db

class Visitor(db.Model):
    """
    Modelo de visitante
    """
    __tablename__ = 'visitors'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    check_ins = db.relationship('VisitorCheckIn', backref='visitor', lazy=True)
    
    def __repr__(self):
        return f'<Visitor {self.name}>'

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
