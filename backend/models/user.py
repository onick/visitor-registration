"""
Modelo para usuarios del sistema
"""
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from .database import db
import secrets

class User(db.Model):
    """
    Modelo para usuarios del sistema
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'staff'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Campos de seguridad adicionales
    login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)
    password_changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    reset_token = db.Column(db.String(255), nullable=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """
        Establece el hash de la contraseña
        """
        self.password_hash = generate_password_hash(password)
        self.password_changed_at = datetime.utcnow()
    
    def check_password(self, password):
        """
        Verifica la contraseña
        """
        return check_password_hash(self.password_hash, password)
    
    def is_account_locked(self):
        """
        Verifica si la cuenta está bloqueada por demasiados intentos de inicio de sesión
        """
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False
    
    def increment_login_attempts(self):
        """
        Incrementa el contador de intentos de inicio de sesión y bloquea la cuenta si es necesario
        """
        self.login_attempts += 1
        
        # Bloquear la cuenta después de 5 intentos fallidos
        if self.login_attempts >= 5:
            # Bloquear por 15 minutos
            self.locked_until = datetime.utcnow() + timedelta(minutes=15)
        
        db.session.commit()
    
    def reset_login_attempts(self):
        """
        Reinicia el contador de intentos de inicio de sesión
        """
        self.login_attempts = 0
        self.locked_until = None
        db.session.commit()
    
    def generate_reset_token(self):
        """
        Genera un token para restablecer la contraseña
        """
        token = secrets.token_urlsafe(32)
        self.reset_token = token
        self.reset_token_expires = datetime.utcnow() + timedelta(hours=24)
        db.session.commit()
        return token
    
    def verify_reset_token(self, token):
        """
        Verifica si el token de restablecimiento es válido
        """
        if not self.reset_token or not self.reset_token_expires:
            return False
        
        if self.reset_token != token:
            return False
        
        if self.reset_token_expires < datetime.utcnow():
            return False
        
        return True
    
    def clear_reset_token(self):
        """
        Limpia el token de restablecimiento
        """
        self.reset_token = None
        self.reset_token_expires = None
        db.session.commit()
    
    @property
    def is_admin(self):
        """
        Verifica si el usuario es administrador
        """
        return self.role == 'admin'
    
    def to_dict(self):
        """
        Convierte el usuario a un diccionario
        """
        return {
            'id': self.id,
            'email': self.email,
            'name': f'{self.first_name} {self.last_name}',
            'role': self.role,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat()
        } 