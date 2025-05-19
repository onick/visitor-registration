#!/usr/bin/env python3
"""
Script para verificar las estadísticas en el dashboard
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

def get_event_statistics(token):
    """Obtener estadísticas de eventos"""
    print("\n2. Obteniendo estadísticas de eventos...")
    
    events_url = f"{API_URL}/events/"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(events_url, headers=headers)
        if response.status_code == 200:
            events = response.json()
            
            # Calcular estadísticas
            total = len(events)
            active = len([e for e in events if e.get('is_active', False)])
            upcoming = len([e for e in events if e.get('is_active', False) and 
                          datetime.fromisoformat(e['start_date'].replace('Z', '+00:00')) > datetime.now()])
            
            print(f"   Total de eventos: {total}")
            print(f"   Eventos activos: {active}")
            print(f"   Eventos próximos: {upcoming}")
            
            return {
                "total": total,
                "active": active,
                "upcoming": upcoming
            }
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    return {"total": 0, "active": 0, "upcoming": 0}

def get_visitor_statistics(token):
    """Obtener estadísticas de visitantes"""
    print("\n3. Obteniendo estadísticas de visitantes...")
    
    # Intentar obtener estadísticas del endpoint específico
    stats_url = f"{API_URL}/visitors/statistics"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(stats_url, headers=headers)
        if response.status_code == 200:
            stats = response.json()
            print(f"   Total de visitantes: {stats.get('total', 0)}")
            print(f"   Check-ins totales: {stats.get('checkedIn', 0)}")
            print(f"   Visitantes hoy: {stats.get('today', 0)}")
            
            # También mostrar estadísticas por evento si están disponibles
            if 'by_event' in stats:
                print("\n   Visitantes por evento:")
                for event_stat in stats.get('by_event', []):
                    print(f"      - {event_stat['event_title']}: {event_stat['visitors_count']} visitantes")
            
            return stats
    except Exception as e:
        print(f"   ✗ Error al obtener estadísticas de visitantes: {e}")
    
    # Fallback: obtener lista de visitantes
    visitors_url = f"{API_URL}/visitors"
    try:
        response = requests.get(visitors_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            visitors = data.get('items', []) if isinstance(data, dict) else data
            print(f"   Total de visitantes (lista): {len(visitors)}")
            return {"total": len(visitors), "checkedIn": 0, "today": 0}
    except Exception as e:
        print(f"   ✗ Error al obtener lista de visitantes: {e}")
    
    return {"total": 0, "checkedIn": 0, "today": 0}

def check_dashboard_data():
    """Verificar los datos que deberían aparecer en el dashboard"""
    print("=== VERIFICACIÓN DE ESTADÍSTICAS DEL DASHBOARD ===")
    
    # Iniciar sesión
    token = login()
    if not token:
        print("\n❌ No se pudo obtener el token")
        return
    
    # Obtener estadísticas
    event_stats = get_event_statistics(token)
    visitor_stats = get_visitor_statistics(token)
    
    print("\n=== RESUMEN PARA EL DASHBOARD ===")
    print("📊 Estadísticas de Eventos:")
    print(f"   - Total: {event_stats['total']}")
    print(f"   - Activos: {event_stats['active']}")
    print(f"   - Próximos: {event_stats['upcoming']}")
    
    print("\n👥 Estadísticas de Visitantes:")
    print(f"   - Total: {visitor_stats.get('total', 0)}")
    print(f"   - Check-ins: {visitor_stats.get('checkedIn', 0)}")
    print(f"   - Hoy: {visitor_stats.get('today', 0)}")
    
    print("\n✅ El dashboard debería mostrar estos datos en:")
    print("   1. Las tarjetas de estadísticas superiores")
    print("   2. Los gráficos de asistencia por evento")
    print("   3. La tendencia de visitantes")
    print("   4. Los eventos recientes")
    print("   5. Los últimos check-ins")

if __name__ == "__main__":
    check_dashboard_data()
