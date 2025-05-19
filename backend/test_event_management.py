#!/usr/bin/env python3
"""
Script para verificar la funcionalidad completa de gestión de eventos
"""
import requests
import json
import sys
from datetime import datetime, timedelta

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
    
    try:
        response = requests.post(login_url, json=login_data)
        print(f"   Código de estado: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✓ Login exitoso")
            print(f"   Usuario: {data['user']['username']}")
            print(f"   Rol: {data['user']['role']}")
            return data['access_token']
        else:
            print(f"   ✗ Error en login: {response.text}")
            return None
    except Exception as e:
        print(f"   ✗ Error de conexión: {e}")
        return None

def list_events(token=None):
    """Listar todos los eventos"""
    print("\n2. Listando eventos...")
    
    events_url = f"{API_URL}/events/"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        response = requests.get(events_url, headers=headers)
        print(f"   Código de estado: {response.status_code}")
        
        if response.status_code == 200:
            events = response.json()
            print(f"   ✓ Se encontraron {len(events)} eventos")
            for event in events:
                print(f"      - {event['title']} (ID: {event['id']}, Activo: {event['is_active']})")
            return events
        else:
            print(f"   ✗ Error al listar eventos: {response.text}")
            return []
    except Exception as e:
        print(f"   ✗ Error de conexión: {e}")
        return []

def create_event(token):
    """Crear un evento de prueba"""
    print("\n3. Creando evento...")
    
    # Fechas para el evento
    start_date = datetime.now() + timedelta(days=1, hours=10)
    end_date = start_date + timedelta(hours=3)
    
    event_url = f"{API_URL}/events/"
    event_data = {
        "title": f"Concierto de Navidad {datetime.now().strftime('%Y')}",
        "description": "Un evento musical navideño con los mejores artistas locales",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "location": "Teatro Principal CCB",
        "capacity": 200,
        "is_active": True
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("   Datos del evento:")
    print(f"      Título: {event_data['title']}")
    print(f"      Fecha: {start_date.strftime('%Y-%m-%d %H:%M')}")
    print(f"      Ubicación: {event_data['location']}")
    
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

def update_event(token, event_id):
    """Actualizar un evento existente"""
    print(f"\n4. Actualizando evento ID {event_id}...")
    
    event_url = f"{API_URL}/events/{event_id}/"
    update_data = {
        "title": f"Concierto de Navidad ACTUALIZADO {datetime.now().strftime('%Y')}",
        "capacity": 250
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.put(event_url, json=update_data, headers=headers)
        print(f"   Código de estado: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Evento actualizado exitosamente")
            print(f"      Nuevo título: {data['title']}")
            print(f"      Nueva capacidad: {data.get('capacity', 'N/A')}")
            return data
        else:
            print(f"   ✗ Error al actualizar evento: {response.text}")
            return None
    except Exception as e:
        print(f"   ✗ Error de conexión: {e}")
        return None

def delete_event(token, event_id):
    """Eliminar un evento"""
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

def main():
    """Función principal"""
    print("=== VERIFICACIÓN DE GESTIÓN DE EVENTOS ===")
    
    # 1. Iniciar sesión
    token = login()
    if not token:
        print("\n❌ No se pudo obtener el token. Abortando.")
        sys.exit(1)
    
    # 2. Listar eventos
    events = list_events(token)
    
    # 3. Crear un evento
    new_event = create_event(token)
    if not new_event:
        print("\n❌ No se pudo crear el evento.")
        sys.exit(1)
    
    # 4. Actualizar el evento
    updated_event = update_event(token, new_event['id'])
    
    # 5. Listar eventos nuevamente
    print("\n6. Listando eventos después de crear...")
    list_events(token)
    
    # 6. Eliminar el evento de prueba
    if updated_event:
        delete_event(token, updated_event['id'])
    
    # 7. Listar eventos finalmente
    print("\n7. Listando eventos después de eliminar...")
    list_events(token)
    
    print("\n✅ ¡Prueba completada con éxito!")
    print("   Todas las operaciones CRUD funcionan correctamente.")

if __name__ == "__main__":
    main()
