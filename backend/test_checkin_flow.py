#!/usr/bin/env python3
"""
Script de prueba para verificar el flujo completo de registro y check-in
"""
import requests
import sys

# Configuración
BASE_URL = "http://localhost:8080/api/v1"

def test_registration_and_checkin():
    """Prueba el flujo completo de registro y check-in"""
    
    print("=== TEST DE REGISTRO Y CHECK-IN ===\n")
    
    # 1. Registrar un visitante
    print("1. Registrando visitante...")
    visitor_data = {
        "name": "Marcelino Francisco",
        "email": "marcelino@ejemplo.com",
        "phone": "809-555-0123",
        "event_id": 1,  # Asumiendo que existe un evento con ID 1
        "kiosk_id": 1
    }
    
    response = requests.post(f"{BASE_URL}/visitors/register", json=visitor_data)
    if response.status_code != 201:
        print(f"✗ Error al registrar visitante: {response.status_code}")
        print(f"  - Respuesta: {response.text}")
        return
    
    registration_data = response.json()
    registration_code = registration_data.get("registration_code")
    visitor_id = registration_data.get("visitor_id")
    
    print(f"✓ Visitante registrado exitosamente")
    print(f"  - ID: {visitor_id}")
    print(f"  - Código de registro: {registration_code}")
    
    # 2. Verificar el código de registro
    print("\n2. Verificando código de registro...")
    verify_data = {
        "code": registration_code
    }
    
    response = requests.post(f"{BASE_URL}/visitors/verify-code", json=verify_data)
    if response.status_code == 200:
        result = response.json()
        visitor_info = result.get('visitor', {})
        events = result.get('events', [])
        
        print(f"✓ Código verificado correctamente")
        print(f"  - Visitante: {visitor_info.get('name')}")
        print(f"  - Email: {visitor_info.get('email')}")
        print(f"  - Eventos disponibles: {len(events)}")
        
        for event in events:
            print(f"    * {event.get('title')} - {event.get('location')}")
    else:
        print(f"✗ Error al verificar código: {response.status_code}")
        print(f"  - Respuesta: {response.text}")
        return
    
    # 3. Verificar con email (debería funcionar también)
    print("\n3. Verificando con email...")
    verify_data = {
        "code": visitor_data["email"]
    }
    
    response = requests.post(f"{BASE_URL}/visitors/verify-code", json=verify_data)
    if response.status_code == 200:
        print("✓ Verificación con email exitosa")
    else:
        print(f"✗ Error al verificar con email: {response.status_code}")
    
    # 4. Verificar con código inválido
    print("\n4. Intentando verificar con código inválido...")
    verify_data = {
        "code": "INVALID"
    }
    
    response = requests.post(f"{BASE_URL}/visitors/verify-code", json=verify_data)
    if response.status_code == 404:
        print("✓ Código inválido rechazado correctamente")
    else:
        print(f"✗ Respuesta inesperada para código inválido: {response.status_code}")
    
    print("\n=== TEST COMPLETADO ===")

def test_event_exists():
    """Verifica que existe al menos un evento"""
    response = requests.get(f"{BASE_URL}/events/")
    if response.status_code == 200:
        events = response.json()
        if len(events) > 0:
            print(f"✓ Hay {len(events)} eventos disponibles")
            for event in events:
                print(f"  - ID: {event['id']}, Título: {event['title']}")
            return True
        else:
            print("✗ No hay eventos disponibles. Creando uno de prueba...")
            return False
    else:
        print(f"✗ Error al obtener eventos: {response.status_code}")
        return False

def create_test_event():
    """Crea un evento de prueba"""
    event_data = {
        "title": "Exposición de Arte",
        "description": "Una exposición de arte contemporáneo",
        "start_date": "2025-06-01T10:00:00Z",
        "end_date": "2025-06-30T18:00:00Z",
        "location": "Sala Principal",
        "is_active": True
    }
    
    response = requests.post(f"{BASE_URL}/events/", json=event_data)
    if response.status_code == 201:
        print("✓ Evento de prueba creado exitosamente")
        return True
    else:
        print(f"✗ Error al crear evento: {response.status_code}")
        print(f"  - Respuesta: {response.text}")
        return False

if __name__ == "__main__":
    print("Verificando conexión con el servidor...")
    try:
        response = requests.get(BASE_URL + "/../")
        if response.status_code == 200:
            print("✓ Servidor conectado\n")
        else:
            print(f"✗ Error de conexión: {response.status_code}")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("✗ No se puede conectar al servidor. Asegúrese de que el backend esté ejecutándose.")
        sys.exit(1)
    
    # Verificar si hay eventos
    if not test_event_exists():
        create_test_event()
    
    # Ejecutar pruebas
    test_registration_and_checkin()
