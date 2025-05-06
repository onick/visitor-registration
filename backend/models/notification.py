"""
Modelo de datos para notificaciones del sistema
"""
from models.database import db
from datetime import datetime

class Notification(db.Model):
    """
    Modelo para notificaciones del sistema
    """
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 'info', 'warning', 'error', 'success'
    for_role = db.Column(db.String(50), nullable=True)  # Rol específico al que va dirigido (None = todos)
    for_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Usuario específico (None = todos)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime, nullable=True)
    
    # Relaciones
    user = db.relationship('User', backref=db.backref('notifications', lazy=True))
    
    def __repr__(self):
        return f'<Notification {self.id} - {self.title}>'
    
    def to_dict(self):
        """
        Convierte la notificación a un diccionario
        """
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'for_role': self.for_role,
            'for_user_id': self.for_user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_read': self.is_read,
            'read_at': self.read_at.isoformat() if self.read_at else None
        } 