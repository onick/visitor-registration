#!/usr/bin/env python3
"""
Script para configurar los kioscos del Centro Cultural Banreservas
Solo se configurarán dos kioscos:
1. Entrada Principal - Para registro y check-in
2. Sala de Realidad Virtual - Para registro y check-in
"""

import sqlite3
from datetime import datetime

def setup_kiosks():
    """Configurar los dos kioscos específicos del sistema"""
    conn = sqlite3.connect('dev.db')
    cursor = conn.cursor()
    
    print("=== Configuración de Kioscos ===\n")
    
    # Primero, limpiar kioscos existentes
    print("Limpiando kioscos existentes...")
    cursor.execute("DELETE FROM kiosk_configs")
    cursor.execute("DELETE FROM kiosks")
    conn.commit()
    
    # Configuración de los kioscos
    kiosks_data = [
        {
            "name": "Kiosco Entrada Principal",
            "location": "Entrada Principal",
            "is_active": 1,
            "config": {
                "language": "es",
                "idle_timeout": 60,
                "custom_message": "Bienvenido al Centro Cultural Banreservas",
                "event_filter": None  # Muestra todos los eventos
            }
        },
        {
            "name": "Kiosco Sala VR",
            "location": "Sala de Realidad Virtual",
            "is_active": 1,
            "config": {
                "language": "es",
                "idle_timeout": 45,  # Timeout más corto para experiencias VR
                "custom_message": "Bienvenido a la Sala de Realidad Virtual",
                "event_filter": None  # Se puede configurar para mostrar solo eventos VR
            }
        }
    ]
    
    # Insertar kioscos y sus configuraciones
    for kiosk_data in kiosks_data:
        # Insertar kiosco
        cursor.execute("""
            INSERT INTO kiosks (name, location, is_active, created_at)
            VALUES (?, ?, ?, ?)
        """, (
            kiosk_data["name"],
            kiosk_data["location"],
            kiosk_data["is_active"],
            datetime.now().isoformat()
        ))
        
        kiosk_id = cursor.lastrowid
        print(f"\n✓ Kiosco creado: {kiosk_data['name']} (ID: {kiosk_id})")
        print(f"  Ubicación: {kiosk_data['location']}")
        print(f"  Estado: {'Activo' if kiosk_data['is_active'] else 'Inactivo'}")
        
        # Insertar configuración
        config = kiosk_data["config"]
        cursor.execute("""
            INSERT INTO kiosk_configs (
                kiosk_id, language, idle_timeout, 
                custom_message, event_filter, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            kiosk_id,
            config["language"],
            config["idle_timeout"],
            config["custom_message"],
            config["event_filter"],
            datetime.now().isoformat()
        ))
        
        print(f"  Configuración:")
        print(f"    - Idioma: {config['language']}")
        print(f"    - Timeout: {config['idle_timeout']} segundos")
        print(f"    - Mensaje: {config['custom_message']}")
    
    conn.commit()
    
    # Verificar la configuración
    print("\n=== Verificación de Kioscos ===")
    cursor.execute("""
        SELECT k.id, k.name, k.location, k.is_active,
               c.language, c.idle_timeout, c.custom_message
        FROM kiosks k
        LEFT JOIN kiosk_configs c ON k.id = c.kiosk_id
        ORDER BY k.id
    """)
    
    kiosks = cursor.fetchall()
    for kiosk in kiosks:
        print(f"\nKiosco ID {kiosk[0]}:")
        print(f"  Nombre: {kiosk[1]}")
        print(f"  Ubicación: {kiosk[2]}")
        print(f"  Activo: {'Sí' if kiosk[3] else 'No'}")
        print(f"  Idioma: {kiosk[4]}")
        print(f"  Timeout: {kiosk[5]}s")
        print(f"  Mensaje: {kiosk[6]}")
    
    conn.close()
    print("\n✓ Configuración de kioscos completada exitosamente")

if __name__ == "__main__":
    setup_kiosks()
