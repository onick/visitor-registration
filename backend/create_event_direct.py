import sqlite3
from datetime import datetime

def create_event():
    # Conectar a la base de datos
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    
    # Verificar si la tabla events existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='events'")
    if not cursor.fetchone():
        # Crear la tabla si no existe
        cursor.execute('''
        CREATE TABLE events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            start_date TIMESTAMP NOT NULL,
            end_date TIMESTAMP NOT NULL,
            location TEXT NOT NULL,
            image_url TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        print("Tabla 'events' creada.")
    
    # Datos del evento
    title = "Recital de Poesía"
    description = "Lectura de poemas de autores dominicanos contemporáneos"
    start_date = "2023-12-01T18:00:00"
    end_date = "2023-12-01T20:00:00"
    location = "Sala de Conferencias"
    is_active = 1
    created_at = datetime.now().isoformat()
    updated_at = created_at
    
    # Insertar el evento
    try:
        cursor.execute('''
        INSERT INTO events (title, description, start_date, end_date, location, is_active, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, description, start_date, end_date, location, is_active, created_at, updated_at))
        
        conn.commit()
        event_id = cursor.lastrowid
        print(f"Evento creado con ID: {event_id}")
        
        # Verificar que el evento fue creado
        cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
        event = cursor.fetchone()
        print(f"Evento creado: {event}")
        
    except Exception as e:
        conn.rollback()
        print(f"Error al crear el evento: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_event() 