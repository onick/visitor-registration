#!/usr/bin/env python3
"""
Script para verificar automáticamente la gestión de eventos desde el frontend
Simula las acciones del navegador para crear y eliminar eventos
"""
import requests
import json
import time
from datetime import datetime, timedelta

# Configuración
FRONTEND_URL = "http://localhost:8094"
API_URL = "http://localhost:8080/api/v1"
USERNAME = "admin"
PASSWORD = "Admin123!"

def login_to_api():
    """Iniciar sesión y obtener token JWT"""
    print("1. Iniciando sesión en la API...")
    
    login_url = f"{API_URL}/auth/login"
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    try:
        response = requests.post(login_url, json=login_data)
        print(f"   Código de estado: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✓ Login exitoso")
            return data['access_token']
        else:
            print(f"   ✗ Error en login: {response.text}")
            return None
    except Exception as e:
        print(f"   ✗ Error de conexión: {e}")
        return None

def verify_frontend_running():
    """Verificar que el frontend esté ejecutándose"""
    print("\n2. Verificando el frontend...")
    
    try:
        response = requests.get(FRONTEND_URL)
        if response.status_code == 200:
            print("   ✓ Frontend está ejecutándose en puerto 8094")
            return True
        else:
            print(f"   ✗ Frontend devolvió código {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ Error de conexión al frontend: {e}")
        return False

def create_event_via_api(token):
    """Crear evento directamente a través de la API para probar el frontend"""
    print("\n3. Creando evento vía API...")
    
    event_url = f"{API_URL}/events/"
    event_data = {
        "title": f"Evento de Prueba Frontend {datetime.now().strftime('%H:%M:%S')}",
        "description": "Evento creado para probar la sincronización con el frontend",
        "start_date": (datetime.now() + timedelta(hours=2)).isoformat(),
        "end_date": (datetime.now() + timedelta(hours=4)).isoformat(),
        "location": "Sala Virtual",
        "capacity": 50,
        "is_active": True
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(event_url, json=event_data, headers=headers)
        print(f"   Código de estado: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"   ✓ Evento creado exitosamente (ID: {data['id']})")
            return data
        else:
            print(f"   ✗ Error al crear evento: {response.text}")
            return None
    except Exception as e:
        print(f"   ✗ Error de conexión: {e}")
        return None

def list_events(token):
    """Listar eventos desde la API"""
    print("\n4. Listando eventos desde la API...")
    
    events_url = f"{API_URL}/events/"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(events_url, headers=headers)
        print(f"   Código de estado: {response.status_code}")
        
        if response.status_code == 200:
            events = response.json()
            print(f"   ✓ Se encontraron {len(events)} eventos")
            active_events = [e for e in events if e.get('is_active', False)]
            print(f"   ✓ Eventos activos: {len(active_events)}")
            return events
        else:
            print(f"   ✗ Error al listar eventos: {response.text}")
            return []
    except Exception as e:
        print(f"   ✗ Error de conexión: {e}")
        return []

def delete_event(token, event_id):
    """Eliminar evento a través de la API"""
    print(f"\n5. Eliminando evento ID {event_id}...")
    
    event_url = f"{API_URL}/events/{event_id}/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.delete(event_url, headers=headers)
        print(f"   Código de estado: {response.status_code}")
        
        if response.status_code == 204:
            print(f"   ✓ Evento eliminado exitosamente")
            return True
        else:
            print(f"   ✗ Error al eliminar evento: {response.text}")
            return False
    except Exception as e:
        print(f"   ✗ Error de conexión: {e}")
        return False

def verify_frontend_sync():
    """Verificar que el frontend sincronice con los cambios del backend"""
    print("\n=== VERIFICACIÓN DE SINCRONIZACIÓN FRONTEND-BACKEND ===")
    
    # 1. Verificar que el frontend esté ejecutándose
    if not verify_frontend_running():
        print("\n❌ El frontend no está disponible")
        return
    
    # 2. Iniciar sesión
    token = login_to_api()
    if not token:
        print("\n❌ No se pudo obtener el token")
        return
    
    # 3. Listar eventos iniciales
    initial_events = list_events(token)
    initial_count = len(initial_events)
    
    # 4. Crear un evento
    new_event = create_event_via_api(token)
    if not new_event:
        print("\n❌ No se pudo crear el evento")
        return
    
    # 5. Verificar que el evento se creó
    time.sleep(1)  # Esperar un momento para sincronización
    after_create_events = list_events(token)
    after_create_count = len(after_create_events)
    
    if after_create_count > initial_count:
        print("   ✓ El evento se reflejó en el backend")
    else:
        print("   ✗ El evento no se reflejó en el backend")
    
    # 6. Eliminar el evento
    delete_event(token, new_event['id'])
    
    # 7. Verificar que el evento se eliminó
    time.sleep(1)  # Esperar un momento para sincronización
    final_events = list_events(token)
    final_count = len(final_events)
    
    if final_count == initial_count:
        print("   ✓ La eliminación se reflejó en el backend")
    else:
        print("   ✗ La eliminación no se reflejó en el backend")
    
    print("\n=== RESUMEN ===")
    print(f"Eventos iniciales: {initial_count}")
    print(f"Eventos después de crear: {after_create_count}")
    print(f"Eventos después de eliminar: {final_count}")
    
    if final_count == initial_count:
        print("\n✅ La sincronización frontend-backend funciona correctamente")
    else:
        print("\n⚠️  Hay problemas con la sincronización")

if __name__ == "__main__":
    verify_frontend_sync()
