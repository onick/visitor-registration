#!/usr/bin/env python3
"""
Script para probar la creación de eventos
"""
import requests
import json
import sys
from datetime import datetime, timedelta

# Configuración
API_URL = "http://localhost:5001/api/v1"
USERNAME = "admin"
PASSWORD = "Admin123!"

def login():
    """Iniciar sesión y obtener token JWT"""
    print("Intentando iniciar sesión...")
    
    login_url = f"{API_URL}/auth/login"
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    try:
        response = requests.post(login_url, json=login_data)
        print(f"Código de estado: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Login exitoso")
            print(f"Usuario: {data['user']['username']}")
            print(f"Rol: {data['user']['role']}")
            return data['access_token']
        else:
            print(f"Error en login: {response.text}")
            return None
    except Exception as e:
        print(f"Error de conexión: {e}")
        return None

def create_event(token):
    """Crear un evento de prueba"""
    print("\nIntentando crear evento...")
    
    # Fechas para el evento (hoy y mañana)
    start_date = datetime.now() + timedelta(hours=1)
    end_date = start_date + timedelta(hours=2)
    
    event_url = f"{API_URL}/events/"
    event_data = {
        "title": "Evento de Prueba",
        "description": "Este es un evento creado para pruebas de diagnóstico",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "location": "Sala de Pruebas",
        "is_active": True
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("Datos del evento:")
    print(json.dumps(event_data, indent=2))
    print("\nHeaders:")
    print(json.dumps(headers, indent=2))
    
    try:
        response = requests.post(event_url, json=event_data, headers=headers)
        print(f"Código de estado: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print("Evento creado exitosamente:")
            print(json.dumps(data, indent=2))
            return data
        else:
            print(f"Error al crear evento: {response.text}")
            return None
    except Exception as e:
        print(f"Error de conexión: {e}")
        return None

def main():
    """Función principal"""
    print("=== PRUEBA DE CREACIÓN DE EVENTOS ===")
    
    # Iniciar sesión
    token = login()
    if not token:
        print("No se pudo obtener el token. Abortando.")
        sys.exit(1)
    
    # Crear evento
    event = create_event(token)
    if not event:
        print("No se pudo crear el evento. Verifique los logs del servidor.")
        sys.exit(1)
    
    print("\n¡Prueba completada con éxito!")

if __name__ == "__main__":
    main() 