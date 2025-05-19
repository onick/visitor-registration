#!/usr/bin/env python3
"""
Test para verificar que el endpoint de eventos devuelve los conteos de registrados
"""

import requests
import json

# URL base del backend
BASE_URL = "http://localhost:8080/api/v1"

def test_events_with_counts():
    """Prueba el endpoint de eventos para verificar que incluye conteos"""
    print("=== Test: Verificando conteos en endpoint de eventos ===\n")
    
    try:
        # Obtener lista de eventos
        response = requests.get(f"{BASE_URL}/events/")
        
        if response.status_code != 200:
            print(f"❌ Error al obtener eventos: Status {response.status_code}")
            return
            
        events = response.json()
        print(f"✅ Se obtuvieron {len(events)} eventos\n")
        
        # Verificar cada evento
        passed = 0
        failed = 0
        
        for i, event in enumerate(events):
            print(f"Evento {i+1}: {event.get('title', 'Sin título')}")
            
            # Verificar campos requeridos
            has_registered = 'registered_count' in event
            has_checked_in = 'checked_in_count' in event
            
            if has_registered and has_checked_in:
                print(f"  ✅ Registrados: {event['registered_count']}")
                print(f"  ✅ Check-ins: {event['checked_in_count']}")
                passed += 1
            else:
                print("  ❌ Faltan campos de conteo:")
                if not has_registered:
                    print("    - Falta 'registered_count'")
                if not has_checked_in:
                    print("    - Falta 'checked_in_count'")
                failed += 1
            print()
        
        # Resumen
        print("=== RESUMEN DEL TEST ===")
        print(f"✅ Eventos con conteos: {passed}")
        print(f"❌ Eventos sin conteos: {failed}")
        
        if failed == 0 and passed > 0:
            print("\n🎉 ¡Todos los eventos tienen conteos correctamente!")
        elif passed == 0:
            print("\n⚠️ Ningún evento tiene conteos. Verifica el código del backend.")
        else:
            print("\n⚠️ Algunos eventos no tienen conteos correctamente.")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor. Asegúrate de que el backend esté ejecutándose.")
    except Exception as e:
        print(f"❌ Error durante el test: {e}")

if __name__ == "__main__":
    test_events_with_counts()
