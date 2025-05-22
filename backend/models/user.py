"""
Modelo para usuarios del sistema
"""
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from .database import db
import secrets
from flask import current_app

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
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=True) # Nueva relación con tabla de roles
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Campos de seguridad adicionales
    login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)
    password_changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    reset_token = db.Column(db.String(255), nullable=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)
    
    # Relaciones
    role_obj = db.relationship('Role', backref=db.backref('users', lazy=True)) # Relación con Role
    
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
        self.login_attempts = (self.login_attempts or 0) + 1
        
        max_attempts = current_app.config.get('MAX_LOGIN_ATTEMPTS', 5)
        lockout_duration = current_app.config.get('ACCOUNT_LOCKOUT_MINUTES', 15)

        if self.login_attempts >= max_attempts:
            self.locked_until = datetime.utcnow() + timedelta(minutes=lockout_duration)
        
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
    
    def has_permission(self, permission_name):
        """
        Verifica si el usuario tiene un permiso específico
        
        Args:
            permission_name (str): Nombre del permiso a verificar
            
        Returns:
            bool: True si tiene el permiso, False en caso contrario
        """
        # Los administradores tienen todos los permisos
        if self.is_admin:
            return True
            
        # Si el usuario tiene rol_obj, verificar permisos
        if self.role_obj:
            for permission in self.role_obj.permissions:
                if permission.name == permission_name:
                    return True
        
        return False
    
    def has_permissions(self, permission_names):
        """
        Verifica si el usuario tiene todos los permisos especificados
        
        Args:
            permission_names (list): Lista de nombres de permisos a verificar
            
        Returns:
            bool: True si tiene todos los permisos, False en caso contrario
        """
        # Los administradores tienen todos los permisos
        if self.is_admin:
            return True
            
        # Si no hay rol_obj, no tiene permisos
        if not self.role_obj:
            return False
            
        # Convertir los permisos a un conjunto para búsqueda rápida
        user_permissions = {p.name for p in self.role_obj.permissions}
        
        # Verificar que todos los permisos requeridos estén en el conjunto
        for permission in permission_names:
            if permission not in user_permissions:
                return False
                
        return True
    
    def to_dict(self):
        """
        Convierte el usuario a un diccionario
        """
        user_dict = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat()
        }
        
        # Agregar permisos si hay role_obj
        if self.role_obj:
            user_dict['permissions'] = [p.name for p in self.role_obj.permissions]
        
        return user_dict 