"""
Script de prueba para verificar la gestión completa de visitantes
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8080/api/v1"

def print_response(response, title):
    """Función helper para imprimir respuestas formateadas"""
    print(f"\n{title}")
    print("=" * 50)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_visitor_management():
    """Probar el flujo completo de gestión de visitantes"""
    
    # 1. Crear un evento de prueba
    print("\n1. CREAR EVENTO DE PRUEBA")
    event_data = {
        "title": "Test Event for Visitor Management",
        "description": "Evento para probar gestión de visitantes",
        "start_date": (datetime.now() + timedelta(days=1)).isoformat(),
        "end_date": (datetime.now() + timedelta(days=1, hours=3)).isoformat(),
        "location": "Sala de Pruebas",
        "is_active": True
    }
    
    response = requests.post(f"{BASE_URL}/events/", json=event_data)
    print_response(response, "Crear evento")
    event = response.json()
    event_id = event['id']
    
    # 2. Registrar múltiples visitantes para el evento
    print("\n2. REGISTRAR VISITANTES PARA EL EVENTO")
    visitors = [
        {
            "name": "María González",
            "email": "maria@example.com",
            "phone": "8095551234",
            "event_id": event_id,
            "kiosk_id": 1
        },
        {
            "name": "Juan Pérez",
            "email": "juan@example.com",
            "phone": "8095555678",
            "event_id": event_id,
            "kiosk_id": 1
        },
        {
            "name": "Ana Martínez",
            "email": "ana@example.com",
            "phone": "8095559999",
            "event_id": event_id,
            "kiosk_id": 1
        }
    ]
    
    for visitor_data in visitors:
        response = requests.post(f"{BASE_URL}/visitors/register", json=visitor_data)
        print_response(response, f"Registrar {visitor_data['name']}")
    
    # 3. Registrar un visitante para otro evento
    print("\n3. CREAR OTRO EVENTO Y REGISTRAR VISITANTE")
    another_event_data = {
        "title": "Otro Evento",
        "description": "Un evento diferente",
        "start_date": (datetime.now() + timedelta(days=2)).isoformat(),
        "end_date": (datetime.now() + timedelta(days=2, hours=2)).isoformat(),
        "location": "Sala B",
        "is_active": True
    }
    
    response = requests.post(f"{BASE_URL}/events/", json=another_event_data)
    another_event = response.json()
    another_event_id = another_event['id']
    
    # Registrar el mismo visitante (María) en otro evento
    visitor_another_event = {
        "name": "María González",
        "email": "maria@example.com",
        "phone": "8095551234",
        "event_id": another_event_id,
        "kiosk_id": 1
    }
    response = requests.post(f"{BASE_URL}/visitors/register", json=visitor_another_event)
    print_response(response, "Registrar María en otro evento")
    
    # 4. Obtener visitantes del primer evento
    print("\n4. OBTENER VISITANTES DEL PRIMER EVENTO")
    response = requests.get(f"{BASE_URL}/visitors/event/{event_id}")
    print_response(response, f"Visitantes del evento {event_id}")
    
    # 5. Obtener visitantes del segundo evento
    print("\n5. OBTENER VISITANTES DEL SEGUNDO EVENTO")
    response = requests.get(f"{BASE_URL}/visitors/event/{another_event_id}")
    print_response(response, f"Visitantes del evento {another_event_id}")
    
    # 6. Buscar visitantes con filtro
    print("\n6. BUSCAR VISITANTES CON FILTRO")
    response = requests.get(f"{BASE_URL}/visitors", params={"search": "María"})
    print_response(response, "Buscar visitantes con nombre 'María'")
    
    # 7. Buscar visitantes de un evento específico
    print("\n7. BUSCAR VISITANTES FILTRADOS POR EVENTO")
    response = requests.get(f"{BASE_URL}/visitors", params={"event_id": event_id})
    print_response(response, f"Visitantes filtrados por evento {event_id}")
    
    # 8. Verificar estadísticas
    print("\n8. OBTENER ESTADÍSTICAS DE VISITANTES")
    response = requests.get(f"{BASE_URL}/visitors/statistics")
    print_response(response, "Estadísticas generales de visitantes")
    
    # 9. Obtener detalles del evento con conteos
    print("\n9. OBTENER DETALLES DEL EVENTO CON CONTEOS")
    response = requests.get(f"{BASE_URL}/events/{event_id}")
    print_response(response, f"Detalles del evento {event_id} con conteos")
    
    # 10. Hacer check-in de un visitante
    print("\n10. HACER CHECK-IN DE UN VISITANTE")
    # Primero obtener el visitor_id de María
    maria_visitor = None
    visitors_response = requests.get(f"{BASE_URL}/visitors", params={"search": "María"})
    if visitors_response.status_code == 200:
        maria_data = visitors_response.json()
        if maria_data['items']:
            maria_visitor = maria_data['items'][0]
            
            # Hacer check-in
            response = requests.post(
                f"{BASE_URL}/events/{event_id}/visitors/{maria_visitor['id']}/checkin"
            )
            print_response(response, "Check-in de María")
    
    # 11. Verificar que el check-in se registró
    print("\n11. VERIFICAR CHECK-IN EN LA LISTA DE VISITANTES")
    response = requests.get(f"{BASE_URL}/visitors/event/{event_id}")
    print_response(response, "Visitantes después del check-in")
    
    print("\n" + "="*50)
    print("PRUEBA COMPLETADA")
    print("="*50)

if __name__ == "__main__":
    test_visitor_management()
