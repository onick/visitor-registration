#!/usr/bin/env python3
"""
Test para verificar que cuando un visitante se registra en un evento,
aparece correctamente en el panel de administración.
"""

import requests
import json
import time
from datetime import datetime, timedelta

# Configuración
BASE_URL = "http://localhost:8080/api/v1"
ADMIN_USER = "admin"
ADMIN_PASS = "Admin123!"

# Colores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

# Headers base
headers = {
    "Content-Type": "application/json"
}

# 1. Login como admin
print_info("Iniciando sesión como administrador...")
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"username": ADMIN_USER, "password": ADMIN_PASS},
    headers=headers
)

if login_response.status_code == 200:
    tokens = login_response.json()
    access_token = tokens.get("access_token")
    headers["Authorization"] = f"Bearer {access_token}"
    print_success("Login exitoso")
else:
    print_error(f"Error al hacer login: {login_response.text}")
    exit(1)

# 2. Crear un evento de prueba
print_info("\nCreando evento de prueba...")
event_data = {
    "title": f"Evento de Prueba - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
    "description": "Evento para probar el registro de visitantes",
    "start_date": datetime.now().isoformat(),
    "end_date": (datetime.now() + timedelta(hours=3)).isoformat(),
    "location": "Sala de Pruebas",
    "is_active": True
}

event_response = requests.post(
    f"{BASE_URL}/events/",
    json=event_data,
    headers=headers
)

if event_response.status_code == 201:
    event = event_response.json()
    event_id = event["id"]
    print_success(f"Evento creado con ID: {event_id}")
else:
    print_error(f"Error al crear evento: {event_response.text}")
    exit(1)

# 3. Usar kiosco existente con ID 1
print_info("\nUsando kiosco existente...")
kiosk_id = 1  # ID del kiosco existente
print_success(f"Usando kiosco con ID: {kiosk_id}")

# 4. Registrar un visitante nuevo y su check-in para el evento
print_info("\nRegistrando visitante y check-in...")
visitor_data = {
    "name": f"Visitante Test {datetime.now().strftime('%H%M%S')}",
    "email": f"test{datetime.now().strftime('%H%M%S')}@example.com",
    "phone": "809-555-0100",
    "event_id": event_id,
    "kiosk_id": kiosk_id
}

# Intentar el registro completo (crear visitante + check-in)
register_response = requests.post(
    f"{BASE_URL}/visitors/register",
    json=visitor_data,
    headers=headers
)

if register_response.status_code == 201:
    register_result = register_response.json()
    visitor_id = register_result.get("visitor_id")
    print_success(f"Visitante registrado con ID: {visitor_id}")
    print_success("Check-in realizado exitosamente")
else:
    print_error(f"Error al registrar visitante: {register_response.text}")
    exit(1)

# 5. Verificar que el visitante aparece en la lista de visitantes del evento
print_info(f"\nVerificando visitantes del evento {event_id}...")
time.sleep(1)  # Pequeña pausa para asegurar que los datos se han guardado

visitors_response = requests.get(
    f"{BASE_URL}/visitors/event/{event_id}",
    headers=headers
)

if visitors_response.status_code == 200:
    visitors = visitors_response.json()
    print_success(f"Número de visitantes encontrados: {len(visitors)}")
    
    # Buscar nuestro visitante
    visitor_found = False
    for visitor in visitors:
        if visitor["id"] == visitor_id:
            visitor_found = True
            print_success(f"Visitante encontrado: {visitor['name']}")
            print_info(f"  - Email: {visitor['email']}")
            print_info(f"  - Teléfono: {visitor['phone']}")
            break
    
    if not visitor_found:
        print_error("El visitante registrado no aparece en la lista del evento")
else:
    print_error(f"Error al obtener visitantes del evento: {visitors_response.text}")

# 6. Verificar con el endpoint de exportación del evento
print_info("\nVerificando con el endpoint de exportación...")
export_response = requests.get(
    f"{BASE_URL}/events/{event_id}/export?format=csv",
    headers=headers
)

if export_response.status_code == 200:
    print_success("Exportación exitosa")
    # Verificar que el contenido incluye nuestro visitante
    csv_content = export_response.text
    if visitor_data["email"] in csv_content:
        print_success("El visitante aparece en los datos exportados")
    else:
        print_warning("El visitante no aparece en los datos exportados")
else:
    print_error(f"Error al exportar datos: {export_response.text}")

# 7. Verificar estadísticas del evento
print_info("\nVerificando estadísticas del evento...")
stats_response = requests.get(
    f"{BASE_URL}/events/{event_id}/statistics",
    headers=headers
)

if stats_response.status_code == 200:
    stats = stats_response.json()
    print_success(f"Estadísticas obtenidas:")
    print_info(f"  - Visitantes registrados: {stats.get('registered', 0)}")
    print_info(f"  - Check-ins: {stats.get('checked_in', 0)}")
elif stats_response.status_code == 404:
    print_warning("El endpoint de estadísticas del evento no existe")
else:
    print_error(f"Error al obtener estadísticas: {stats_response.text}")

# 8. Limpiar (opcional)
print("\n¿Desea eliminar los datos de prueba? (s/n): ", end="")
response = input().strip().lower()
if response == 's':
    # Eliminar evento (esto también eliminará los check-ins asociados)
    delete_response = requests.delete(
        f"{BASE_URL}/events/{event_id}",
        headers=headers
    )
    
    if delete_response.status_code == 204:
        print_success("Evento eliminado")
    else:
        print_error(f"Error al eliminar evento: {delete_response.text}")

print_info("\n✨ Prueba completada")
