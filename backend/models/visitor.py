"""
Modelo para visitantes
"""
from datetime import datetime
import secrets
import string
import json
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
    registration_code = db.Column(db.String(10), unique=True, nullable=False)
    # Campo interests comentado para evitar errores con la base de datos PostgreSQL
    # interests = db.Column(db.Text, default='[]')  # Intereses almacenados como JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    check_ins = db.relationship('VisitorCheckIn', backref='visitor', lazy=True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.registration_code:
            self.registration_code = self.generate_unique_code()
        # if 'interests' not in kwargs and not self.interests:
        #    self.interests = '[]'
    
    @staticmethod
    def generate_unique_code():
        """Genera un código único de 6 caracteres alfanuméricos"""
        characters = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(secrets.choice(characters) for _ in range(6))
            # Verificar que el código no exista
            if not Visitor.query.filter_by(registration_code=code).first():
                return code
    
    # Comentamos estas funciones para evitar problemas con la base de datos PostgreSQL
    # def get_interests(self):
    #     """Obtener lista de intereses desde el campo JSON"""
    #     try:
    #         return json.loads(self.interests)
    #     except:
    #         return []
    # 
    # def set_interests(self, interests_list):
    #     """Establecer intereses como JSON"""
    #     self.interests = json.dumps(interests_list)
    # 
    # def add_interest(self, interest):
    #     """Añadir un nuevo interés si no existe"""
    #     interests = self.get_interests()
    #     if interest not in interests:
    #         interests.append(interest)
    #         self.set_interests(interests)
    # 
    # def calculate_interests(self, db_session):
    #     """Calcular intereses basados en el historial de visitas"""
    #     # Obtener tipos de eventos visitados
    #     event_types = db_session.query(Event.type).join(
    #         VisitorCheckIn, 
    #         VisitorCheckIn.event_id == Event.id
    #     ).filter(
    #         VisitorCheckIn.visitor_id == self.id
    #     ).group_by(Event.type).all()
    #     
    #     # Contar visitas por tipo
    #     type_counts = {}
    #     for event_type in event_types:
    #         type_counts[event_type[0]] = db_session.query(VisitorCheckIn).join(
    #             Event, 
    #             VisitorCheckIn.event_id == Event.id
    #         ).filter(
    #             VisitorCheckIn.visitor_id == self.id,
    #             Event.type == event_type[0]
    #         ).count()
    #     
    #     # Actualizar intereses si un tipo tiene ≥ 2 visitas
    #     interests = []
    #     for event_type, count in type_counts.items():
    #         if count >= 2:
    #             interests.append(event_type)
    #     
    #     self.set_interests(interests)
    
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

