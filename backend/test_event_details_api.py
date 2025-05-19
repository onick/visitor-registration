#!/usr/bin/env python3
"""
Script para verificar que el endpoint de detalles del evento funciona correctamente
"""
import requests
import json

# Configuración
API_URL = "http://localhost:8080/api/v1"

def test_event_details():
    """Probar el endpoint de detalles del evento"""
    print("=== Prueba de Detalles del Evento ===\n")
    
    # 1. Obtener lista de eventos
    print("1. Obteniendo lista de eventos...")
    try:
        response = requests.get(f"{API_URL}/events/")
        response.raise_for_status()
        events = response.json()
        print(f"✅ {len(events)} eventos encontrados")
        
        if not events:
            print("❌ No hay eventos disponibles para probar")
            return
        
        # Tomar el primer evento
        event = events[0]
        event_id = event['id']
        print(f"\nUsando evento: {event['title']} (ID: {event_id})")
        
    except Exception as e:
        print(f"❌ Error al obtener eventos: {e}")
        return
    
    # 2. Obtener detalles del evento
    print(f"\n2. Obteniendo detalles del evento {event_id}...")
    try:
        response = requests.get(f"{API_URL}/events/{event_id}")
        response.raise_for_status()
        event_details = response.json()
        print("✅ Detalles del evento obtenidos:")
        print(json.dumps(event_details, indent=2))
        
    except Exception as e:
        print(f"❌ Error al obtener detalles: {e}")
        return
    
    # 3. Obtener visitantes del evento
    print(f"\n3. Obteniendo visitantes del evento {event_id}...")
    try:
        response = requests.get(f"{API_URL}/visitors/event/{event_id}")
        response.raise_for_status()
        visitors = response.json()
        print(f"✅ {len(visitors)} visitantes encontrados")
        
        if visitors:
            print("\nPrimeros 3 visitantes:")
            for i, visitor in enumerate(visitors[:3]):
                print(f"  - {visitor['name']} ({visitor['email']})")
        
    except Exception as e:
        print(f"❌ Error al obtener visitantes: {e}")
        return
    
    # 4. Obtener estadísticas del evento
    print(f"\n4. Obteniendo estadísticas del evento {event_id}...")
    try:
        response = requests.get(f"{API_URL}/events/{event_id}/statistics")
        response.raise_for_status()
        stats = response.json()
        print("✅ Estadísticas del evento:")
        print(json.dumps(stats, indent=2))
        
    except Exception as e:
        print(f"❌ Error al obtener estadísticas: {e}")
        print("   (Este endpoint puede no estar implementado)")
    
    print("\n✅ Prueba completada exitosamente")
    print("\nVerifica que estos datos aparezcan en la vista de detalles del evento en el frontend")

if __name__ == "__main__":
    test_event_details()
