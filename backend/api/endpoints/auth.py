"""
Endpoints para autenticación de usuarios
"""
from flask_restx import Namespace, Resource, fields
from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token, 
    jwt_required, get_jwt_identity
)
from models.user import User
from models.database import db
from models.notification import Notification
from datetime import datetime, timedelta
from utils.decorators import role_required
from utils.email_service import send_email
import os

auth_namespace = Namespace('auth', description='Operaciones de autenticación')

# Modelos para la documentación de la API
login_model = auth_namespace.model('Login', {
    'username': fields.String(required=True, description='Nombre de usuario'),
    'password': fields.String(required=True, description='Contraseña')
})

register_model = auth_namespace.model('Register', {
    'username': fields.String(required=True, description='Nombre de usuario'),
    'email': fields.String(required=True, description='Correo electrónico'),
    'password': fields.String(required=True, description='Contraseña'),
    'first_name': fields.String(required=True, description='Nombre'),
    'last_name': fields.String(required=True, description='Apellido'),
    'role': fields.String(required=True, description='Rol (admin o staff)')
})

token_model = auth_namespace.model('Token', {
    'access_token': fields.String(description='Token de acceso JWT'),
    'refresh_token': fields.String(description='Token de refresco JWT'),
    'user': fields.Raw(description='Información del usuario')
})

refresh_model = auth_namespace.model('Refresh', {
    'refresh_token': fields.String(required=True, description='Token de refresco JWT')
})

password_reset_request_model = auth_namespace.model('PasswordResetRequest', {
    'email': fields.String(required=True, description='Correo electrónico')
})

password_reset_model = auth_namespace.model('PasswordReset', {
    'token': fields.String(required=True, description='Token de restablecimiento'),
    'email': fields.String(required=True, description='Correo electrónico'),
    'new_password': fields.String(required=True, description='Nueva contraseña')
})

change_password_model = auth_namespace.model('ChangePassword', {
    'current_password': fields.String(required=True, description='Contraseña actual'),
    'new_password': fields.String(required=True, description='Nueva contraseña')
})

@auth_namespace.route('/login')
class Login(Resource):
    """
    Endpoint para iniciar sesión
    """
    @auth_namespace.doc('login')
    @auth_namespace.expect(login_model)
    @auth_namespace.marshal_with(token_model, code=200)
    def post(self):
        """
        Iniciar sesión con nombre de usuario y contraseña
        """
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        # Validar campos requeridos
        if not username or not password:
            return {'error': 'Nombre de usuario y contraseña son requeridos'}, 400
        
        # Buscar usuario
        user = User.query.filter_by(username=username).first()
        
        # Si el usuario no existe
        if not user:
            return {'error': 'Credenciales inválidas'}, 401
        
        # Verificar si la cuenta está activa
        if not user.is_active:
            return {'error': 'Cuenta desactivada. Contacte al administrador'}, 401
        
        # Verificar si la cuenta está bloqueada
        if user.is_account_locked():
            lock_time = user.locked_until - datetime.utcnow()
            minutes = int(lock_time.total_seconds() / 60)
            return {'error': f'Cuenta bloqueada temporalmente. Intente nuevamente en {minutes} minutos'}, 401
        
        # Verificar contraseña
        if not user.check_password(password):
            # Incrementar contador de intentos fallidos
            user.increment_login_attempts()
            
            # Si la cuenta se bloquea después de este intento
            if user.is_account_locked():
                return {'error': 'Demasiados intentos fallidos. Cuenta bloqueada por 15 minutos'}, 401
            
            return {'error': 'Credenciales inválidas'}, 401
        
        # Inicio de sesión exitoso, resetear contador de intentos
        user.reset_login_attempts()
        
        # Actualizar tiempo de último inicio de sesión
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Generar tokens - asegurarse de que identity sea un string
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        # Crear notificación de nuevo inicio de sesión
        notification = Notification(
            title='Nuevo inicio de sesión',
            message=f'Has iniciado sesión el {datetime.utcnow().strftime("%Y-%m-%d %H:%M")}',
            type='info',
            for_user_id=user.id
        )
        db.session.add(notification)
        db.session.commit()
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }

@auth_namespace.route('/register')
class Register(Resource):
    """
    Endpoint para registrar nuevos usuarios
    """
    @auth_namespace.doc('register', security='apikey')
    @auth_namespace.expect(register_model)
    @jwt_required()
    @role_required(['admin'])
    def post(self):
        """
        Registrar un nuevo usuario (Solo administradores)
        """
        data = request.json
        
        # Validar campos requeridos
        required_fields = ['username', 'email', 'password', 'first_name', 'last_name', 'role']
        for field in required_fields:
            if field not in data or not data[field]:
                return {'error': f'El campo {field} es requerido'}, 400
        
        # Validar rol
        if data['role'] not in ['admin', 'staff']:
            return {'error': 'Rol inválido. Use: admin, staff'}, 400
        
        # Verificar si el usuario ya existe
        if User.query.filter_by(username=data['username']).first():
            return {'error': 'El nombre de usuario ya está en uso'}, 400
        
        if User.query.filter_by(email=data['email']).first():
            return {'error': 'El correo electrónico ya está en uso'}, 400
        
        # Crear nuevo usuario
        new_user = User(
            username=data['username'],
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=data['role'],
            is_active=True,
            created_at=datetime.utcnow()
        )
        new_user.set_password(data['password'])
        
        db.session.add(new_user)
        db.session.commit()
        
        return new_user.to_dict(), 201

@auth_namespace.route('/refresh')
class Refresh(Resource):
    """
    Endpoint para renovar token de acceso
    """
    @auth_namespace.doc('refresh')
    @auth_namespace.expect(refresh_model)
    def post(self):
        """
        Renovar token de acceso usando token de refresco
        """
        data = request.json
        refresh_token = data.get('refresh_token')
        
        if not refresh_token:
            return {'error': 'Token de refresco es requerido'}, 400
        
        try:
            # Verificar identidad desde token
            identity = get_jwt_identity()
            
            # Generar nuevo token de acceso
            new_access_token = create_access_token(identity=str(identity))
            
            return {'access_token': new_access_token}, 200
        except Exception as e:
            return {'error': 'Token de refresco inválido'}, 401

@auth_namespace.route('/me')
class UserInfo(Resource):
    """
    Endpoint para obtener información del usuario actual
    """
    @auth_namespace.doc('me', security='apikey')
    @jwt_required()
    def get(self):
        """
        Obtener información del usuario actual
        """
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return {'error': 'Usuario no encontrado'}, 404
        
        return user.to_dict()

@auth_namespace.route('/change-password')
class ChangePassword(Resource):
    """
    Endpoint para cambiar contraseña
    """
    @auth_namespace.doc('change_password', security='apikey')
    @auth_namespace.expect(change_password_model)
    @jwt_required()
    def post(self):
        """
        Cambiar contraseña del usuario actual
        """
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return {'error': 'Usuario no encontrado'}, 404
        
        data = request.json
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        # Validar campos requeridos
        if not current_password or not new_password:
            return {'error': 'Contraseña actual y nueva son requeridas'}, 400
        
        # Verificar contraseña actual
        if not user.check_password(current_password):
            return {'error': 'Contraseña actual incorrecta'}, 400
        
        # Verificar que la nueva contraseña sea diferente
        if current_password == new_password:
            return {'error': 'La nueva contraseña debe ser diferente a la actual'}, 400
        
        # Verificar complejidad de la contraseña
        if len(new_password) < 8:
            return {'error': 'La contraseña debe tener al menos 8 caracteres'}, 400
        
        # Cambiar contraseña
        user.set_password(new_password)
        db.session.commit()
        
        # Crear notificación de cambio de contraseña
        notification = Notification(
            title='Contraseña actualizada',
            message='Tu contraseña ha sido actualizada exitosamente',
            type='success',
            for_user_id=user.id
        )
        db.session.add(notification)
        db.session.commit()
        
        return {'message': 'Contraseña actualizada exitosamente'}, 200

@auth_namespace.route('/password-reset-request')
class PasswordResetRequest(Resource):
    """
    Endpoint para solicitar restablecimiento de contraseña
    """
    @auth_namespace.doc('password_reset_request')
    @auth_namespace.expect(password_reset_request_model)
    def post(self):
        """
        Solicitar restablecimiento de contraseña
        """
        data = request.json
        email = data.get('email')
        
        if not email:
            return {'error': 'Correo electrónico es requerido'}, 400
        
        # Buscar usuario
        user = User.query.filter_by(email=email).first()
        
        # No revelar si el usuario existe o no por razones de seguridad
        if not user:
            return {'message': 'Si el correo existe, recibirás instrucciones para restablecer tu contraseña'}, 200
        
        # Generar token
        token = user.generate_reset_token()
        
        # Enviar correo con instrucciones
        reset_url = f"{os.environ.get('FRONTEND_URL', 'http://localhost:3000')}/reset-password?token={token}&email={email}"
        
        email_body = f"""
        <h2>Restablecimiento de Contraseña</h2>
        <p>Has solicitado restablecer tu contraseña. Haz clic en el siguiente enlace:</p>
        <p><a href="{reset_url}">Restablecer Contraseña</a></p>
        <p>Si no solicitaste este cambio, ignora este mensaje.</p>
        <p>El enlace expirará en 24 horas.</p>
        """
        
        try:
            send_email(
                to=email,
                subject="Restablecimiento de Contraseña - Centro Cultural Banreservas",
                html_content=email_body
            )
        except Exception as e:
            # En un entorno de desarrollo, puede que no se envíe el correo
            print(f"Error al enviar correo: {str(e)}")
        
        return {'message': 'Si el correo existe, recibirás instrucciones para restablecer tu contraseña'}, 200

@auth_namespace.route('/password-reset')
class PasswordReset(Resource):
    """
    Endpoint para restablecer contraseña
    """
    @auth_namespace.doc('password_reset')
    @auth_namespace.expect(password_reset_model)
    def post(self):
        """
        Restablecer contraseña con token
        """
        data = request.json
        token = data.get('token')
        email = data.get('email')
        new_password = data.get('new_password')
        
        # Validar campos requeridos
        if not token or not email or not new_password:
            return {'error': 'Token, correo y nueva contraseña son requeridos'}, 400
        
        # Buscar usuario
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return {'error': 'Solicitud inválida'}, 400
        
        # Verificar token
        if not user.verify_reset_token(token):
            return {'error': 'Token inválido o expirado'}, 400
        
        # Verificar complejidad de la contraseña
        if len(new_password) < 8:
            return {'error': 'La contraseña debe tener al menos 8 caracteres'}, 400
        
        # Cambiar contraseña
        user.set_password(new_password)
        user.clear_reset_token()
        db.session.commit()
        
        # Crear notificación de cambio de contraseña
        notification = Notification(
            title='Contraseña restablecida',
            message='Tu contraseña ha sido restablecida exitosamente',
            type='success',
            for_user_id=user.id
        )
        db.session.add(notification)
        db.session.commit()
        
        return {'message': 'Contraseña restablecida exitosamente'}, 200

# Solo para pruebas en desarrollo
if os.environ.get('FLASK_ENV') == 'development':
    @auth_namespace.route('/test/password-reset-token/<email>')
    class TestPasswordResetToken(Resource):
        def get(self, email):
            user = User.query.filter_by(email=email).first()
            if not user or not user.reset_token:
                return {'error': 'No hay token disponible'}, 404
            return {'token': user.reset_token}, 200 