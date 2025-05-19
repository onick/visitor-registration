from app import create_app
from models.database import db
from models.user import User
import datetime

app = create_app()

with app.app_context():
    # Buscar el usuario admin
    admin = User.query.filter_by(email='admin@ccb.do').first()
    
    if admin:
        print(f"Usuario encontrado: {admin.username}")
        print(f"Email: {admin.email}")
        print(f"Rol: {admin.role}")
        print(f"Activo: {admin.is_active}")
        print(f"Intentos de inicio de sesión: {admin.login_attempts}")
        print(f"Bloqueado hasta: {admin.locked_until}")
        
        # Reiniciar intentos de inicio de sesión y desbloquear
        admin.login_attempts = 0
        admin.locked_until = None
        
        # Cambiar la contraseña
        admin.set_password('Admin123!')
        
        db.session.commit()
        print("Contraseña restablecida a 'Admin123!' y cuenta desbloqueada")
    else:
        print("No se encontró un usuario con el correo admin@ccb.do")