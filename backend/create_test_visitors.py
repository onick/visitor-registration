#!/usr/bin/env python3
"""
Script para crear visitantes de prueba con códigos de registro
"""

import sqlite3
from datetime import datetime, timedelta

def create_test_visitors():
    """Crear visitantes de prueba y registrarlos a eventos"""
    conn = sqlite3.connect('dev.db')
    cursor = conn.cursor()
    
    # Obtener eventos activos
    cursor.execute("SELECT id, title FROM event WHERE is_active = 1")
    events = cursor.fetchall()
    
    if not events:
        print("No hay eventos activos. Creando uno de prueba...")
        # Crear evento de prueba
        start_date = datetime.now()
        end_date = start_date + timedelta(hours=3)
        
        cursor.execute("""
            INSERT INTO event (title, description, start_date, end_date, location, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "Concierto de Jazz",
            "Una noche de jazz con músicos locales",
            start_date.isoformat(),
            end_date.isoformat(),
            "Auditorio Principal",
            1
        ))
        event_id = cursor.lastrowid
        events = [(event_id, "Concierto de Jazz")]
    
    # Visitantes de prueba
    test_visitors = [
        {
            "name": "Juan Pérez",
            "email": "juan.perez@ejemplo.com",
            "phone": "809-555-0001"
        },
        {
            "name": "María García",
            "email": "maria.garcia@ejemplo.com",
            "phone": "809-555-0002"
        },
        {
            "name": "Pedro Rodríguez",
            "email": "pedro.rodriguez@ejemplo.com",
            "phone": "809-555-0003"
        },
        {
            "name": "Ana Martínez",
            "email": "ana.martinez@ejemplo.com",
            "phone": "809-555-0004"
        },
        {
            "name": "Luis Sánchez",
            "email": "luis.sanchez@ejemplo.com",
            "phone": "809-555-0005"
        }
    ]
    
    print("\n=== Creando visitantes de prueba ===")
    
    for visitor_data in test_visitors:
        # Verificar si el visitante ya existe
        cursor.execute("SELECT id FROM visitor WHERE email = ?", (visitor_data["email"],))
        existing = cursor.fetchone()
        
        if existing:
            visitor_id = existing[0]
            print(f"Visitante existente: {visitor_data['name']} (ID: {visitor_id})")
        else:
            # Crear nuevo visitante
            cursor.execute("""
                INSERT INTO visitor (name, email, phone, created_at)
                VALUES (?, ?, ?, ?)
            """, (
                visitor_data["name"],
                visitor_data["email"],
                visitor_data["phone"],
                datetime.now().isoformat()
            ))
            visitor_id = cursor.lastrowid
            print(f"Visitante creado: {visitor_data['name']} (ID: {visitor_id})")
        
        # Registrar visitante al primer evento activo
        event_id = events[0][0]
        event_title = events[0][1]
        
        # Verificar si ya está registrado
        cursor.execute("""
            SELECT id FROM visitor_check_in 
            WHERE visitor_id = ? AND event_id = ?
        """, (visitor_id, event_id))
        
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO visitor_check_in (visitor_id, event_id, kiosk_id, check_in_time)
                VALUES (?, ?, ?, ?)
            """, (visitor_id, event_id, 1, None))
            print(f"  -> Registrado para: {event_title}")
        else:
            print(f"  -> Ya registrado para: {event_title}")
    
    conn.commit()
    
    print("\n=== Códigos de acceso para check-in ===")
    print("Los visitantes pueden usar cualquiera de estos códigos:")
    print("- Su ID numérico (ej: 1, 2, 3)")
    print("- Su email completo")
    print("- Su número de teléfono")
    
    print("\n=== Lista de visitantes y sus códigos ===")
    cursor.execute("""
        SELECT id, name, email, phone 
        FROM visitor 
        ORDER BY id
    """)
    
    for visitor in cursor.fetchall():
        print(f"\n{visitor[1]}:")
        print(f"  - ID: {visitor[0]}")
        print(f"  - Email: {visitor[2]}")
        print(f"  - Teléfono: {visitor[3]}")
    
    conn.close()
    print("\n✓ Visitantes de prueba creados exitosamente")

if __name__ == "__main__":
    create_test_visitors()
