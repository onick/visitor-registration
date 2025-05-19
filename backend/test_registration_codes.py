"""
Script para probar el sistema de códigos de registro
"""
import requests
import json

BASE_URL = "http://localhost:8080/api/v1"

def test_registration_codes():
    print("=== Prueba del Sistema de Códigos de Registro ===\n")
    
    # 1. Registrar un nuevo visitante
    print("1. Registrando un nuevo visitante...")
    visitor_data = {
        "name": "María González",
        "email": "maria.gonzalez@example.com",
        "phone": "809-555-1234",
        "event_id": 1  # Asumiendo que existe un evento con ID 1
    }
    
    response = requests.post(f"{BASE_URL}/visitors/register", json=visitor_data)
    if response.status_code == 201:
        result = response.json()
        registration_code = result.get('registration_code')
        visitor_id = result.get('visitor_id')
        print(f"✓ Visitante registrado con éxito")
        print(f"  - ID: {visitor_id}")
        print(f"  - Código de registro: {registration_code}")
        print(f"  - Mensaje: {result.get('message')}")
    else:
        print(f"✗ Error al registrar visitante: {response.status_code}")
        print(f"  - Respuesta: {response.text}")
        return
    
    print("\n2. Verificando código de registro...")
    # 2. Verificar el código de registro
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
    
    print("\n3. Verificando con email...")
    # 3. Verificar con email
    verify_data = {
        "code": visitor_data["email"]
    }
    
    response = requests.post(f"{BASE_URL}/visitors/verify-code", json=verify_data)
    if response.status_code == 200:
        print("✓ Verificación con email exitosa")
    else:
        print(f"✗ Error al verificar con email: {response.status_code}")
    
    print("\n4. Verificando con teléfono...")
    # 4. Verificar con teléfono
    verify_data = {
        "code": visitor_data["phone"]
    }
    
    response = requests.post(f"{BASE_URL}/visitors/verify-code", json=verify_data)
    if response.status_code == 200:
        print("✓ Verificación con teléfono exitosa")
    else:
        print(f"✗ Error al verificar con teléfono: {response.status_code}")
    
    print("\n5. Intentando verificar con código inválido...")
    # 5. Verificar con código inválido
    verify_data = {
        "code": "INVALID"
    }
    
    response = requests.post(f"{BASE_URL}/visitors/verify-code", json=verify_data)
    if response.status_code == 404:
        print("✓ Código inválido rechazado correctamente")
    else:
        print(f"✗ Respuesta inesperada para código inválido: {response.status_code}")

if __name__ == "__main__":
    test_registration_codes()
