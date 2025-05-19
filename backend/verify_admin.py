"""
Script para verificar y corregir el usuario administrador
"""
from app import create_app
from models.database import db
from models.user import User
import datetime

app = create_app()

with app.app_context():
    # Buscar el usuario admin por email
    admin = User.query.filter_by(email='admin@ccb.do').first()
    
    if admin:
        print(f"Usuario encontrado por email: {admin.email}")
        print(f"Username actual: {admin.username}")
        print(f"¿Está activo?: {admin.is_active}")
        print(f"Intentos de login: {admin.login_attempts}")
        
        # Asegurarnos de que el username es 'admin'
        if admin.username != 'admin':
            print(f"Cambiando username de '{admin.username}' a 'admin'")
            admin.username = 'admin'
            db.session.commit()
            print("¡Username actualizado a 'admin'!")
        
        # Reiniciar la contraseña y asegurar que la cuenta está activa
        admin.set_password('Admin123!')
        admin.is_active = True
        admin.login_attempts = 0
        admin.locked_until = None
        db.session.commit()
        print("Contraseña restablecida a 'Admin123!' y cuenta desbloqueada")
        
        print("\n--- INSTRUCCIONES DE INICIO DE SESIÓN ---")
        print("Usa exactamente estas credenciales:")
        print("Username: admin")
        print("Contraseña: Admin123!")
    else:
        print("No se encontró un usuario con el correo admin@ccb.do")
        
        # Crear un nuevo administrador si no existe
        print("Creando nuevo usuario administrador...")
        new_admin = User(
            username="admin",
            email="admin@ccb.do",
            first_name="Administrador",
            last_name="Sistema",
            role="admin",
            is_active=True,
            created_at=datetime.datetime.utcnow()
        )
        new_admin.set_password('Admin123!')
        db.session.add(new_admin)
        db.session.commit()
        print("Nuevo usuario administrador creado:")
        print("Username: admin")
        print("Contraseña: Admin123!")
