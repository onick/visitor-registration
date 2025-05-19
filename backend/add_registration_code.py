"""
Script para agregar el campo registration_code a la tabla visitors
"""
import sqlite3
import string
import secrets

def generate_unique_code():
    """Genera un código único de 6 caracteres alfanuméricos"""
    characters = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(characters) for _ in range(6))

def migrate_database():
    # Conectar a la base de datos
    conn = sqlite3.connect('dev.db')
    cursor = conn.cursor()
    
    try:
        # Verificar si la columna ya existe
        cursor.execute("PRAGMA table_info(visitors)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'registration_code' not in columns:
            print("Agregando columna registration_code...")
            
            # Agregar la columna
            cursor.execute("ALTER TABLE visitors ADD COLUMN registration_code VARCHAR(10)")
            
            # Obtener todos los visitantes existentes
            cursor.execute("SELECT id FROM visitors")
            visitor_ids = cursor.fetchall()
            
            # Generar códigos únicos para visitantes existentes
            print(f"Generando códigos para {len(visitor_ids)} visitantes existentes...")
            
            used_codes = set()
            for visitor_id in visitor_ids:
                while True:
                    code = generate_unique_code()
                    if code not in used_codes:
                        used_codes.add(code)
                        cursor.execute(
                            "UPDATE visitors SET registration_code = ? WHERE id = ?",
                            (code, visitor_id[0])
                        )
                        break
            
            conn.commit()
            print("Migración completada exitosamente!")
        else:
            print("La columna registration_code ya existe. No se requiere migración.")
            
    except Exception as e:
        print(f"Error durante la migración: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
