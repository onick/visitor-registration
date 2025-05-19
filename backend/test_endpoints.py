#!/usr/bin/env python3
"""
Script para probar los endpoints del backend
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8080/api/v1"

def test_login():
    """Probar endpoint de login"""
    print("=== Probando Login ===")
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "admin",
        "password": "Admin123!"
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.json().get("access_token")

def test_get_events():
    """Probar obtener eventos"""
    print("\n=== Probando GET Eventos ===")
    response = requests.get(f"{BASE_URL}/events/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.json()

def test_register_visitor(event_id):
    """Probar registro de visitante"""
    print("\n=== Probando Registro de Visitante ===")
    response = requests.post(f"{BASE_URL}/visitors/register", json={
        "name": "Juan Pérez",
        "email": "juan@example.com",
        "phone": "809-555-1234",
        "event_id": event_id,
        "kiosk_id": 1
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.json()

def test_get_statistics():
    """Probar estadísticas de visitantes"""
    print("\n=== Probando Estadísticas ===")
    response = requests.get(f"{BASE_URL}/visitors/statistics")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.json()

def test_get_visitors():
    """Probar obtener visitantes"""
    print("\n=== Probando GET Visitantes ===")
    response = requests.get(f"{BASE_URL}/visitors")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.json()

if __name__ == "__main__":
    # Probar login
    token = test_login()
    
    # Obtener eventos
    events = test_get_events()
    
    if events and len(events) > 0:
        event_id = events[0]["id"]
        
        # Registrar visitante
        test_register_visitor(event_id)
        
        # Obtener estadísticas
        test_get_statistics()
        
        # Obtener visitantes
        test_get_visitors()
    else:
        print("No hay eventos disponibles")
