"""
Script simple para corregir el usuario administrador
"""
import os
import sys
import sqlite3

# Conectar a la base de datos
conn = sqlite3.connect('dev.db')
cursor = conn.cursor()

# Verificar si el usuario admin existe
cursor.execute("SELECT id, username, email, is_active, role FROM users WHERE email = 'admin@ccb.do'")
admin = cursor.fetchone()

if admin:
    admin_id = admin[0]
    print(f"Usuario encontrado: ID={admin_id}, username={admin[1]}, email={admin[2]}, activo={admin[3]}, rol={admin[4]}")
    
    # Actualizar el username a 'admin' si es diferente
    if admin[1] != 'admin':
        cursor.execute("UPDATE users SET username = 'admin' WHERE id = ?", (admin_id,))
        print("Username actualizado a 'admin'")
    
    # Asegurar que la cuenta está activa y sin bloqueos
    cursor.execute("""
        UPDATE users 
        SET is_active = 1, 
            login_attempts = 0, 
            locked_until = NULL,
            password_hash = 'pbkdf2:sha256:260000$TByvkLgQsXfI2HaO$8b0fe3a24fac27ff1219719c42e15297fa66fe9c67332efac09af2a35e8f4aa1'
        WHERE id = ?
    """, (admin_id,))
    
    print("Cuenta actualizada:")
    print("- Password restablecido a 'Admin123!'")
    print("- Cuenta activada y desbloqueada")
else:
    print("No se encontró el usuario admin@ccb.do, creando uno nuevo...")
    
    # Crear un nuevo usuario admin
    cursor.execute("""
        INSERT INTO users (username, email, password_hash, first_name, last_name, role, is_active, created_at)
        VALUES ('admin', 'admin@ccb.do', 'pbkdf2:sha256:260000$TByvkLgQsXfI2HaO$8b0fe3a24fac27ff1219719c42e15297fa66fe9c67332efac09af2a35e8f4aa1',
                'Administrador', 'Sistema', 'admin', 1, datetime('now'))
    """)
    
    print("Nuevo usuario administrador creado:")
    print("Username: admin")
    print("Email: admin@ccb.do")
    print("Contraseña: Admin123!")

# Guardar los cambios
conn.commit()
conn.close()

print("\n--- INSTRUCCIONES DE INICIO DE SESIÓN ---")
print("Usa exactamente estas credenciales:")
print("Username: admin")
print("Contraseña: Admin123!")
print("\nIMPORTANTE: En la pantalla de login, aunque diga 'Correo Electrónico', debes escribir 'admin', NO 'admin@ccb.do'")
