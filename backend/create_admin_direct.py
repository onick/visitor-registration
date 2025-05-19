"""
Script para crear un usuario administrador directamente en la base de datos
"""
import os
import sys
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash

# Determinar la ruta de la base de datos
db_path = 'dev.db'  # Base de datos SQLite por defecto

# Verificar si el archivo existe
if not os.path.exists(db_path):
    print(f"Error: La base de datos '{db_path}' no existe.")
    sys.exit(1)

# Establecer la contraseña para el admin
admin_password = "Admin123!"
# Generar el hash de la contraseña manualmente
password_hash = generate_password_hash(admin_password)

# Conectar a la base de datos
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Verificar si existe la tabla users
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if not cursor.fetchone():
        print("Creando tabla de usuarios...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            role TEXT NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            login_attempts INTEGER DEFAULT 0,
            locked_until TIMESTAMP,
            password_changed_at TIMESTAMP,
            reset_token TEXT,
            reset_token_expires TIMESTAMP
        )
        ''')

    # Comprobar tablas disponibles
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("Tablas disponibles en la base de datos:")
    for table in tables:
        print(f"- {table[0]}")

    # Eliminar usuario admin existente si ya existe
    cursor.execute("DELETE FROM users WHERE username = 'admin' OR email = 'admin@ccb.do'")
    affected = cursor.rowcount
    if affected > 0:
        print(f"Se eliminaron {affected} usuarios administradores antiguos")

    # Crear nuevo usuario admin
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
    INSERT INTO users (
        username, password_hash, email, first_name, last_name, 
        role, is_active, created_at, password_changed_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', ('admin', password_hash, 'admin@ccb.do', 'Administrador', 'Sistema', 
          'admin', 1, now, now))
    
    # Guardar cambios
    conn.commit()
    print("¡Usuario administrador creado exitosamente!")
    print("\nCredenciales de acceso:")
    print("Username: admin")
    print("Email: admin@ccb.do")
    print("Contraseña: Admin123!")
    print("\nIMPORTANTE: Intenta iniciar sesión con 'admin' en el campo donde dice 'Correo Electrónico'")
    
    # Verificar que el usuario se creó correctamente
    cursor.execute("SELECT id, username, email, is_active, role FROM users WHERE username = 'admin'")
    user = cursor.fetchone()
    if user:
        print("\nVerificación de usuario creado:")
        print(f"ID: {user[0]}")
        print(f"Username: {user[1]}")
        print(f"Email: {user[2]}")
        print(f"Activo: {user[3]}")
        print(f"Rol: {user[4]}")
    else:
        print("\n¡ADVERTENCIA! No se pudo verificar que el usuario se haya creado correctamente.")

except Exception as e:
    conn.rollback()
    print(f"Error: {str(e)}")
finally:
    conn.close()
