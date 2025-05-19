#!/usr/bin/env python3
"""
Script para probar el flujo completo de registro y confirmación
"""
import requests
import json
from datetime import datetime

# Configuración
API_URL = "http://localhost:8080/api/v1"
USERNAME = "admin"
PASSWORD = "Admin123!"

def login():
    """Iniciar sesión y obtener token JWT"""
    print("1. Iniciando sesión...")
    
    login_url = f"{API_URL}/auth/login"
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    response = requests.post(login_url, json=login_data)
    if response.status_code == 200:
        data = response.json()
        print("   ✓ Login exitoso")
        return data['access_token']
    else:
        print(f"   ✗ Error en login: {response.text}")
        return None

def register_visitor(token):
    """Registrar un visitante para probar la confirmación"""
    print("\n2. Registrando visitante de prueba...")
    
    # Primero obtener un evento activo
    events_url = f"{API_URL}/events/"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(events_url, headers=headers)
    events = response.json()
    active_events = [e for e in events if e.get('is_active', False)]
    
    if not active_events:
        print("   ✗ No hay eventos activos")
        return None
    
    event = active_events[0]
    print(f"   Usando evento: {event['title']} (ID: {event['id']})")
    
    # Registrar visitante
    visitor_data = {
        "name": "Juan Pérez Test",
        "email": f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
        "phone": "809-555-0123",
        "event_id": event['id'],
        "kiosk_id": 1
    }
    
    register_url = f"{API_URL}/visitors/register"
    
    try:
        response = requests.post(register_url, json=visitor_data, headers=headers)
        if response.status_code == 201:
            print("   ✓ Visitante registrado exitosamente")
            print(f"   Datos enviados:")
            print(f"      - Nombre: {visitor_data['name']}")
            print(f"      - Email: {visitor_data['email']}")
            print(f"      - Evento: {event['title']}")
            print(f"      - ID Evento: {event['id']}")
            
            return {
                "visitor_name": visitor_data['name'],
                "event_id": event['id'],
                "event_name": event['title'],
                "response": response.json()
            }
        else:
            print(f"   ✗ Error al registrar: {response.text}")
            return None
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return None

def check_registration_flow():
    """Verificar el flujo completo de registro"""
    print("=== VERIFICACIÓN DEL FLUJO DE REGISTRO Y CONFIRMACIÓN ===")
    
    # Iniciar sesión
    token = login()
    if not token:
        print("\n❌ No se pudo obtener el token")
        return
    
    # Registrar visitante
    registration = register_visitor(token)
    if not registration:
        print("\n❌ No se pudo registrar el visitante")
        return
    
    print("\n3. Datos para la página de confirmación:")
    print(f"   - Nombre del visitante: {registration['visitor_name']}")
    print(f"   - ID del evento: {registration['event_id']}")
    print(f"   - Nombre del evento: {registration['event_name']}")
    
    print("\n4. Para probar en el navegador:")
    print("   1. Ve a http://localhost:8094")
    print("   2. Ve a la sección de eventos")
    print("   3. Registra un visitante")
    print("   4. Verifica que la página de confirmación muestre:")
    print(f"      - Nombre: {registration['visitor_name']}")
    print(f"      - Evento: {registration['event_name']}")
    print("      - Código: [código generado]")
    
    print("\n✅ Registro completado. Verifica la página de confirmación en el navegador.")

if __name__ == "__main__":
    check_registration_flow()
