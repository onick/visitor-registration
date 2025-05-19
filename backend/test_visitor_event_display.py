"""
Script de prueba para verificar que los visitantes muestren el evento correcto
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8080/api/v1"

def test_visitor_event_display():
    """Probar que los visitantes muestren correctamente su evento"""
    
    # 1. Obtener lista de visitantes
    print("\n1. OBTENIENDO LISTA DE VISITANTES")
    response = requests.get(f"{BASE_URL}/visitors")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Respuesta: {json.dumps(data, indent=2)}")
        
        if 'items' in data:
            visitors = data['items']
            print(f"\nTotal de visitantes: {len(visitors)}")
            
            # Mostrar información de cada visitante
            for visitor in visitors:
                print(f"\nVisitante: {visitor.get('name')}")
                print(f"  - ID: {visitor.get('id')}")
                print(f"  - Email: {visitor.get('email')}")
                print(f"  - Teléfono: {visitor.get('phone')}")
                print(f"  - Código: {visitor.get('registration_code')}")
                
                # Verificar información del evento
                if 'event' in visitor and visitor['event']:
                    event = visitor['event']
                    print(f"  - Evento ID: {event.get('id')}")
                    print(f"  - Evento Título: {event.get('title')}")
                    print(f"  - Evento Fecha: {event.get('start_date')}")
                    print(f"  - Evento Lugar: {event.get('location')}")
                elif 'event_title' in visitor:
                    print(f"  - Evento: {visitor.get('event_title')}")
                else:
                    print("  - Evento: SIN EVENTO ASIGNADO")
                
                print(f"  - Check-in: {'Sí' if visitor.get('checked_in') else 'No'}")
        else:
            print("La respuesta no contiene 'items'")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
    
    # 2. Crear un evento de prueba
    print("\n\n2. CREANDO EVENTO DE PRUEBA")
    event_data = {
        "title": "Evento Test para Visitantes",
        "description": "Evento de prueba para verificar asociación con visitantes",
        "start_date": datetime.now().isoformat(),
        "end_date": (datetime.now().replace(hour=20)).isoformat(),
        "location": "Sala Principal",
        "is_active": True
    }
    
    response = requests.post(f"{BASE_URL}/events/", json=event_data)
    if response.status_code == 201:
        event = response.json()
        event_id = event['id']
        print(f"Evento creado con ID: {event_id}")
        
        # 3. Registrar visitante para este evento
        print("\n3. REGISTRANDO VISITANTE PARA EL EVENTO")
        visitor_data = {
            "name": "Test Visitor para Evento",
            "email": f"test.visitor.{int(datetime.now().timestamp())}@example.com",
            "phone": "809-555-0123",
            "event_id": event_id,
            "kiosk_id": 1
        }
        
        response = requests.post(f"{BASE_URL}/visitors/register", json=visitor_data)
        print(f"Status: {response.status_code}")
        print(f"Respuesta: {json.dumps(response.json(), indent=2)}")
        
        # 4. Obtener lista de visitantes nuevamente
        print("\n4. OBTENIENDO LISTA ACTUALIZADA DE VISITANTES")
        response = requests.get(f"{BASE_URL}/visitors")
        if response.status_code == 200:
            data = response.json()
            if 'items' in data:
                visitors = data['items']
                # Buscar el visitante recién creado
                for visitor in visitors:
                    if visitor.get('email') == visitor_data['email']:
                        print(f"\nVisitante encontrado:")
                        print(f"  - Nombre: {visitor.get('name')}")
                        print(f"  - Email: {visitor.get('email')}")
                        
                        if 'event' in visitor and visitor['event']:
                            event = visitor['event']
                            print(f"  - Evento ID: {event.get('id')}")
                            print(f"  - Evento Título: {event.get('title')}")
                        elif 'event_title' in visitor:
                            print(f"  - Evento: {visitor.get('event_title')}")
                        else:
                            print("  - Evento: NO SE MUESTRA EL EVENTO")
    
    # 5. Probar filtro por evento
    print("\n\n5. PROBANDO FILTRO POR EVENTO")
    response = requests.get(f"{BASE_URL}/visitors", params={"event_id": event_id})
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if 'items' in data:
            visitors = data['items']
            print(f"Visitantes del evento {event_id}: {len(visitors)}")
            for visitor in visitors:
                print(f"  - {visitor.get('name')} - Evento: {visitor.get('event_title', 'N/A')}")

if __name__ == "__main__":
    test_visitor_event_display()
