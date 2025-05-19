#!/usr/bin/env python3
"""
Script para verificar que solo se muestran eventos activos
"""
import requests
import json
from datetime import datetime, timedelta

# Configuración
API_URL = "http://localhost:8080/api/v1"
USERNAME = "admin"
PASSWORD = "Admin123!"

def login():
    """Iniciar sesión y obtener token JWT"""
    login_url = f"{API_URL}/auth/login"
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    response = requests.post(login_url, json=login_data)
    if response.status_code == 200:
        data = response.json()
        return data['access_token']
    return None

def create_test_events(token):
    """Crear eventos de prueba: uno activo y uno inactivo"""
    print("Creando eventos de prueba...")
    
    event_url = f"{API_URL}/events/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Evento ACTIVO
    active_event = {
        "title": "Evento ACTIVO de Prueba",
        "description": "Este evento debe aparecer en la lista",
        "start_date": (datetime.now() + timedelta(days=1)).isoformat(),
        "end_date": (datetime.now() + timedelta(days=1, hours=2)).isoformat(),
        "location": "Sala Principal",
        "capacity": 100,
        "is_active": True
    }
    
    response1 = requests.post(event_url, json=active_event, headers=headers)
    if response1.status_code == 201:
        print("   ✓ Evento ACTIVO creado (ID:", response1.json()['id'], ")")
    
    # Evento INACTIVO
    inactive_event = {
        "title": "Evento INACTIVO de Prueba",
        "description": "Este evento NO debe aparecer en la lista filtrada",
        "start_date": (datetime.now() + timedelta(days=2)).isoformat(),
        "end_date": (datetime.now() + timedelta(days=2, hours=2)).isoformat(),
        "location": "Sala Secundaria",
        "capacity": 50,
        "is_active": False
    }
    
    response2 = requests.post(event_url, json=inactive_event, headers=headers)
    if response2.status_code == 201:
        print("   ✓ Evento INACTIVO creado (ID:", response2.json()['id'], ")")

def list_all_events(token):
    """Listar todos los eventos sin filtrar"""
    print("\nListando TODOS los eventos...")
    
    events_url = f"{API_URL}/events/"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(events_url, headers=headers)
    if response.status_code == 200:
        events = response.json()
        print(f"Total de eventos: {len(events)}")
        for event in events:
            print(f"   - {event['title']} (ID: {event['id']}, Activo: {event['is_active']})")
        
        active_count = len([e for e in events if e['is_active']])
        inactive_count = len([e for e in events if not e['is_active']])
        
        print(f"\nResumen:")
        print(f"   Eventos activos: {active_count}")
        print(f"   Eventos inactivos: {inactive_count}")
        return events
    return []

def main():
    print("=== VERIFICACIÓN DE FILTRO DE EVENTOS ACTIVOS ===")
    
    # Iniciar sesión
    token = login()
    if not token:
        print("Error al iniciar sesión")
        return
    
    # Crear eventos de prueba
    create_test_events(token)
    
    # Listar todos los eventos
    events = list_all_events(token)
    
    print("\n🔍 VERIFICACIÓN:")
    print("En el frontend, la vista de eventos debería mostrar:")
    print(f"   - Solo {len([e for e in events if e['is_active']])} eventos activos")
    print("   - NO debería mostrar eventos con is_active = False")
    print("\n📱 Para verificar el frontend:")
    print("1. Abre http://localhost:8094 en el navegador")
    print("2. Inicia sesión como admin")
    print("3. Ve a la sección 'Ver Eventos'")
    print("4. Verifica que solo se muestren eventos activos")

if __name__ == "__main__":
    main()
