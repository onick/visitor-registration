"""
Modelo para kioscos
"""
from datetime import datetime
from .database import db

class Kiosk(db.Model):
    """
    Modelo de kiosco de auto-registro
    """
    __tablename__ = 'kiosks'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    last_heartbeat = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    config = db.relationship('KioskConfig', backref='kiosk', lazy=True, uselist=False)
    check_ins = db.relationship('VisitorCheckIn', backref='kiosk', lazy=True)
    
    def __repr__(self):
        return f'<Kiosk {self.name}>'
    
    @property
    def is_online(self):
        """
        Verificar si el kiosco está en línea basado en su último heartbeat
        """
        if not self.last_heartbeat:
            return False
        
        time_diff = datetime.utcnow() - self.last_heartbeat
        return time_diff.total_seconds() < 300  # 5 minutos

class KioskConfig(db.Model):
    """
    Configuración de kiosco
    """
    __tablename__ = 'kiosk_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    kiosk_id = db.Column(db.Integer, db.ForeignKey('kiosks.id'), nullable=False, unique=True)
    language = db.Column(db.String(10), default='es')
    idle_timeout = db.Column(db.Integer, default=60)  # segundos
    event_filter = db.Column(db.String(255))
    custom_message = db.Column(db.Text)
    logo_url = db.Column(db.String(500))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<KioskConfig kiosk_id={self.kiosk_id}>'
