"""
Servicio de autenticación
"""
from flask_jwt_extended import create_access_token, create_refresh_token
from models.user import User
from models.database import db
from datetime import datetime, timedelta

class AuthService:
    @staticmethod
    def authenticate(email, password):
        """
        Autenticar a un usuario y generar tokens JWT
        """
        user = User.query.filter_by(email=email, is_active=True).first()
        
        if user and user.check_password(password):
            # Actualizar último login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Crear tokens
            access_token = create_access_token(
                identity=str(user.id),
                additional_claims={
                    'role': user.role,
                    'email': user.email
                }
            )
            
            refresh_token = create_refresh_token(
                identity=str(user.id),
                additional_claims={
                    'role': user.role,
                    'email': user.email
                }
            )
            
            return {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user.to_dict()
            }
        
        return None
    
    @staticmethod
    def register_user(email, password, name, role='staff'):
        """
        Registrar un nuevo usuario
        """
        # Verificar si el usuario ya existe
        if User.query.filter_by(email=email).first():
            return None
        
        # Crear nuevo usuario
        user = User(
            email=email,
            name=name,
            role=role
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return user.to_dict()
    
    @staticmethod
    def refresh_token(user_id):
        """
        Generar nuevo token de acceso usando token de actualización
        """
        user = User.query.get(user_id)
        
        if user and user.is_active:
            access_token = create_access_token(
                identity=str(user.id),
                additional_claims={
                    'role': user.role,
                    'email': user.email
                }
            )
            
            return {
                'access_token': access_token,
                'user': user.to_dict()
            }
        
        return None
    
    @staticmethod
    def change_password(user_id, current_password, new_password):
        """
        Cambiar contraseña del usuario
        """
        user = User.query.get(user_id)
        
        if user and user.check_password(current_password):
            user.set_password(new_password)
            db.session.commit()
            return True
        
        return False
    
    @staticmethod
    def create_initial_admin(email, password, name):
        """
        Crear usuario administrador inicial si no existe ninguno
        """
        # Verificar si ya existe algún admin
        if User.query.filter_by(role='admin').first():
            return None
        
        # Crear usuario admin
        admin = User(
            email=email,
            name=name,
            role='admin'
        )
        admin.set_password(password)
        
        db.session.add(admin)
        db.session.commit()
        
        return admin.to_dict() 