"""
Script para simular la experiencia completa del usuario:
1. Registrar un visitante para un evento
2. Verificar que aparece en el panel de administración
"""

import time
import requests
import json
from datetime import datetime, timedelta
import webbrowser

# Configuración
BASE_URL = "http://localhost:8080/api/v1"
FRONTEND_URL = "http://localhost:8094"
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
    "title": f"Evento Demo - {datetime.now().strftime('%Y%m%d_%H%M')}",
    "description": "Evento para demostrar el registro de visitantes",
    "start_date": datetime.now().isoformat(),
    "end_date": (datetime.now() + timedelta(hours=3)).isoformat(),
    "location": "Sala Principal",
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
    print_info(f"  Título: {event['title']}")
    print_info(f"  Ubicación: {event['location']}")
else:
    print_error(f"Error al crear evento: {event_response.text}")
    exit(1)

# 3. Registrar algunos visitantes
print_info("\nRegistrando visitantes de prueba...")
visitors_to_create = [
    {
        "name": "Juan Pérez",
        "email": "juan.perez@example.com",
        "phone": "809-555-0101"
    },
    {
        "name": "María García",
        "email": "maria.garcia@example.com",
        "phone": "809-555-0102"
    },
    {
        "name": "Carlos Rodríguez",
        "email": "carlos.rodriguez@example.com",
        "phone": "809-555-0103"
    }
]

visitor_ids = []
for visitor_data in visitors_to_create:
    # Agregar IDs del evento y kiosco
    visitor_data["event_id"] = event_id
    visitor_data["kiosk_id"] = 1
    
    register_response = requests.post(
        f"{BASE_URL}/visitors/register",
        json=visitor_data,
        headers=headers
    )
    
    if register_response.status_code == 201:
        result = register_response.json()
        visitor_ids.append(result["visitor_id"])
        print_success(f"  Registrado: {visitor_data['name']}")
    else:
        if "ya está registrado" in register_response.text:
            print_warning(f"  {visitor_data['name']} ya estaba registrado")
        else:
            print_error(f"  Error al registrar {visitor_data['name']}: {register_response.text}")

# 4. Verificar que los visitantes aparecen en el panel admin
print_info("\nVerificando visitantes en el panel de administración...")
visitors_response = requests.get(
    f"{BASE_URL}/visitors/event/{event_id}",
    headers=headers
)

if visitors_response.status_code == 200:
    visitors = visitors_response.json()
    print_success(f"Visitantes encontrados: {len(visitors)}")
    
    for visitor in visitors:
        print_info(f"  - {visitor['name']} ({visitor['email']})")
        print_info(f"    Check-in: {'Sí' if visitor['checked_in'] else 'No'}")
else:
    print_error(f"Error al obtener visitantes: {visitors_response.text}")

# 5. Generar URLs para acceder al frontend
print_info("\n📱 URLs para verificar manualmente:")
print_info(f"Panel administrativo: {FRONTEND_URL}/admin")
print_info(f"  Usuario: {ADMIN_USER}")
print_info(f"  Contraseña: {ADMIN_PASS}")
print_info(f"\nVer detalles del evento: {FRONTEND_URL}/admin/events/{event_id}")
print_info(f"Kiosco de registro: {FRONTEND_URL}/kiosk")

# 6. Mostrar resumen
print_info("\n📊 RESUMEN:")
print_success(f"Evento: {event['title']}")
print_success(f"Visitantes registrados: {len(visitors)}")
print_info("\nPuedes verificar en el panel de administración que:")
print_info("1. El evento aparece en la lista de eventos")
print_info("2. Al hacer clic en el evento, puedes ver los visitantes registrados")
print_info("3. Los visitantes aparecen con su información completa")

# Preguntar si abrir el navegador
response = input("\n¿Deseas abrir el navegador en el panel de administración? (s/n): ")
if response.lower() == 's':
    admin_url = f"{FRONTEND_URL}/admin/events/{event_id}"
    print_info(f"Abriendo {admin_url} en el navegador...")
    webbrowser.open(admin_url)

print_info("\n✨ Prueba completada")
