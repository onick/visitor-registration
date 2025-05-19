"""
Script para reiniciar la base de datos y crear un nuevo usuario administrador
"""
import os
import sys
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash
import subprocess
import json

# Configuración
DB_PATH = 'dev.db'
API_URL = 'http://localhost:8080/api/v1'
ADMIN_USER = 'admin'
ADMIN_PASSWORD = 'Admin123!'

# Colores para salida
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'

def print_colored(text, color):
    """Imprime texto con color"""
    print(f"{color}{text}{Colors.ENDC}")

def reset_database():
    """Elimina y recrea la base de datos"""
    print_colored("Reiniciando base de datos...", Colors.YELLOW)
    
    # Eliminar base de datos si existe
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print_colored(f"Base de datos {DB_PATH} eliminada", Colors.YELLOW)
    
    # Crear nueva base de datos
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Crear tabla de usuarios
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
    
    # Crear tabla de kiosks
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS kiosks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        location TEXT NOT NULL,
        is_active BOOLEAN DEFAULT 1,
        last_heartbeat TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Crear un kiosk por defecto
    cursor.execute('''
    INSERT INTO kiosks (name, location, is_active) 
    VALUES (?, ?, ?)
    ''', ('Kiosk Principal', 'Entrada', 1))
    
    conn.commit()
    print_colored("Base de datos creada con éxito", Colors.GREEN)
    return conn, cursor

def create_admin_user(conn, cursor):
    """Crear usuario administrador"""
    print_colored(f"Creando usuario administrador '{ADMIN_USER}'...", Colors.YELLOW)
    
    # Generar hash de la contraseña
    password_hash = generate_password_hash(ADMIN_PASSWORD)
    
    # Fecha actual
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    
    # Insertar usuario administrador
    cursor.execute('''
    INSERT INTO users (
        username, password_hash, email, first_name, last_name, 
        role, is_active, created_at, password_changed_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (ADMIN_USER, password_hash, 'admin@ccb.do', 'Administrador', 'Sistema', 
          'admin', 1, now, now))
    
    conn.commit()
    print_colored(f"Usuario administrador creado exitosamente", Colors.GREEN)
    print_colored(f"  Usuario: {ADMIN_USER}", Colors.BLUE)
    print_colored(f"  Contraseña: {ADMIN_PASSWORD}", Colors.BLUE)
    
    # Verificar el usuario creado
    cursor.execute("SELECT id, username, email, role FROM users WHERE username = ?", (ADMIN_USER,))
    user = cursor.fetchone()
    if user:
        print_colored(f"  ID: {user[0]}", Colors.BLUE)
        print_colored(f"  Username: {user[1]}", Colors.BLUE)
        print_colored(f"  Email: {user[2]}", Colors.BLUE)
        print_colored(f"  Rol: {user[3]}", Colors.BLUE)
        return True
    else:
        print_colored("Error: No se pudo verificar la creación del usuario", Colors.RED)
        return False

def test_login():
    """Probar inicio de sesión con curl"""
    print_colored("\nProbando inicio de sesión con API...", Colors.YELLOW)
    
    try:
        # Ejecutar comando curl
        command = [
            'curl', '-s', '-X', 'POST', 
            f'{API_URL}/auth/login', 
            '-H', 'Content-Type: application/json', 
            '-d', f'{{"username":"{ADMIN_USER}","password":"{ADMIN_PASSWORD}"}}'
        ]
        
        result = subprocess.run(command, capture_output=True, text=True)
        
        # Verificar respuesta
        if result.returncode != 0:
            print_colored(f"Error en la ejecución de curl: {result.stderr}", Colors.RED)
            return False
        
        try:
            # Intentar parsear la respuesta como JSON
            response = json.loads(result.stdout)
            
            if 'access_token' in response and 'user' in response:
                print_colored("Inicio de sesión exitoso:", Colors.GREEN)
                print_colored(f"  Usuario: {response['user']['username']}", Colors.BLUE)
                print_colored(f"  Rol: {response['user']['role']}", Colors.BLUE)
                print_colored(f"  Token obtenido: {response['access_token'][:20]}...", Colors.BLUE)
                return True
            else:
                print_colored(f"Error: Respuesta inválida: {response}", Colors.RED)
                return False
        except json.JSONDecodeError:
            print_colored(f"Error: No se pudo decodificar la respuesta JSON", Colors.RED)
            print_colored(f"Respuesta: {result.stdout}", Colors.RED)
            return False
            
    except Exception as e:
        print_colored(f"Error al probar inicio de sesión: {str(e)}", Colors.RED)
        return False

def print_instructions():
    """Mostrar instrucciones para el usuario"""
    print_colored("\n========================================================", Colors.GREEN)
    print_colored(" INSTRUCCIONES PARA INICIAR SESIÓN", Colors.GREEN)
    print_colored("========================================================", Colors.GREEN)
    print_colored("1. Abre el navegador y ve a http://localhost:8106/login", Colors.BLUE)
    print_colored("2. Ingresa las siguientes credenciales:", Colors.BLUE)
    print_colored(f"   - Nombre de Usuario: {ADMIN_USER}", Colors.BLUE)
    print_colored(f"   - Contraseña: {ADMIN_PASSWORD}", Colors.BLUE)
    print_colored("3. Asegúrate de que el backend esté corriendo en el puerto 8080", Colors.BLUE)
    print_colored("4. Asegúrate de que el frontend esté corriendo en el puerto 8106", Colors.BLUE)
    print_colored("========================================================", Colors.GREEN)
    print_colored("IMPORTANTE: Si sigues teniendo problemas:", Colors.YELLOW)
    print_colored("- Intenta abrir el navegador en modo incógnito", Colors.YELLOW)
    print_colored("- Reinicia el backend y el frontend", Colors.YELLOW)
    print_colored("- Verifica que no haya errores en la consola del navegador", Colors.YELLOW)
    print_colored("========================================================", Colors.GREEN)

def main():
    """Función principal"""
    print_colored("\n========== REPARACIÓN DE ACCESO AL SISTEMA ==========", Colors.GREEN)
    
    # Reiniciar base de datos
    conn, cursor = reset_database()
    
    # Crear usuario administrador
    success = create_admin_user(conn, cursor)
    
    # Cerrar conexión a la base de datos
    conn.close()
    
    if success:
        # Probar inicio de sesión
        login_success = test_login()
        
        if login_success:
            print_colored("\n¡Reparación completada con éxito!", Colors.GREEN)
            print_instructions()
        else:
            print_colored("\nLa reparación fue parcial, el usuario se creó pero hay problemas con el inicio de sesión.", Colors.YELLOW)
            print_colored("Revisa que el servidor backend esté corriendo y que la configuración del API_URL sea correcta.", Colors.YELLOW)
    else:
        print_colored("\nLa reparación falló, no se pudo crear el usuario administrador.", Colors.RED)

if __name__ == "__main__":
    main()
