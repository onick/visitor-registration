"""
Pruebas de integración para el flujo de registro de visitantes
"""
import pytest
from datetime import datetime, timedelta

class TestVisitorRegistrationFlow:
    """
    Pruebas de integración para el flujo completo de registro de visitantes
    """
    
    def test_complete_visitor_registration_flow(self, client, admin_token, auth_headers):
        """
        Prueba del flujo completo de registro de visitantes:
        1. Crear un evento
        2. Crear un kiosco
        3. Registrar un visitante en el evento
        4. Verificar que el visitante aparece en la lista de visitantes del evento
        """
        # 1. Crear un evento como administrador
        event_data = {
            'title': 'Evento de Integración',
            'description': 'Descripción del evento de integración',
            'start_date': (datetime.utcnow() + timedelta(days=1)).isoformat(),
            'end_date': (datetime.utcnow() + timedelta(days=1, hours=8)).isoformat(),
            'location': 'Ubicación del evento de integración',
            'is_active': True
        }
        
        event_response = client.post(
            '/api/v1/events/',
            json=event_data,
            headers=auth_headers(admin_token)
        )
        
        assert event_response.status_code == 201
        event_id = event_response.json['id']
        
        # 2. Crear un kiosco como administrador
        kiosk_data = {
            'name': 'Kiosco de Integración',
            'location': 'Ubicación del kiosco de integración',
            'is_active': True
        }
        
        kiosk_response = client.post(
            '/api/v1/kiosks/',
            json=kiosk_data,
            headers=auth_headers(admin_token)
        )
        
        assert kiosk_response.status_code == 201
        kiosk_id = kiosk_response.json['id']
        
        # 3. Registrar un visitante para el evento
        registration_data = {
            'name': 'Visitante de Integración',
            'email': 'visitante.integracion@test.com',
            'phone': '+1234567890',
            'event_id': event_id,
            'kiosk_id': kiosk_id
        }
        
        registration_response = client.post('/api/v1/visitors/register', json=registration_data)
        
        assert registration_response.status_code == 201
        visitor_id = registration_response.json['visitor_id']
        
        # 4. Verificar que el visitante aparece en la lista de visitantes del evento
        visitors_response = client.get(
            f'/api/v1/visitors/event/{event_id}',
            headers=auth_headers(admin_token)
        )
        
        assert visitors_response.status_code == 200
        assert isinstance(visitors_response.json, list)
        assert len(visitors_response.json) >= 1
        
        visitor_found = False
        for visitor in visitors_response.json:
            if visitor['id'] == visitor_id:
                visitor_found = True
                assert visitor['name'] == 'Visitante de Integración'
                assert visitor['email'] == 'visitante.integracion@test.com'
        
        assert visitor_found, "El visitante registrado no se encontró en la lista de visitantes del evento"
    
    def test_admin_overview_flow(self, client, admin_token, auth_headers):
        """
        Prueba del flujo de visualización para administradores:
        1. Crear un evento
        2. Crear un kiosco
        3. Registrar varios visitantes
        4. Verificar estadísticas
        5. Verificar estado de kioscos
        """
        # 1. Crear un evento como administrador
        event_data = {
            'title': 'Evento Estadísticas',
            'description': 'Descripción del evento para estadísticas',
            'start_date': (datetime.utcnow() + timedelta(days=2)).isoformat(),
            'end_date': (datetime.utcnow() + timedelta(days=2, hours=8)).isoformat(),
            'location': 'Ubicación del evento para estadísticas',
            'is_active': True
        }
        
        event_response = client.post(
            '/api/v1/events/',
            json=event_data,
            headers=auth_headers(admin_token)
        )
        
        assert event_response.status_code == 201
        event_id = event_response.json['id']
        
        # 2. Crear un kiosco como administrador
        kiosk_data = {
            'name': 'Kiosco Estadísticas',
            'location': 'Ubicación del kiosco para estadísticas',
            'is_active': True
        }
        
        kiosk_response = client.post(
            '/api/v1/kiosks/',
            json=kiosk_data,
            headers=auth_headers(admin_token)
        )
        
        assert kiosk_response.status_code == 201
        kiosk_id = kiosk_response.json['id']
        
        # 3. Registrar varios visitantes
        visitor_names = ["Ana García", "Pedro Méndez", "María Rodríguez"]
        visitor_emails = ["ana@test.com", "pedro@test.com", "maria@test.com"]
        
        for i in range(3):
            registration_data = {
                'name': visitor_names[i],
                'email': visitor_emails[i],
                'phone': f'+123456789{i}',
                'event_id': event_id,
                'kiosk_id': kiosk_id
            }
            
            registration_response = client.post('/api/v1/visitors/register', json=registration_data)
            assert registration_response.status_code == 201
        
        # 4. Verificar estadísticas
        stats_response = client.get(
            '/api/v1/visitors/stats',
            headers=auth_headers(admin_token)
        )
        
        assert stats_response.status_code == 200
        assert stats_response.json['total_visitors'] >= 3
        assert stats_response.json['total_check_ins'] >= 3
        
        # 5. Verificar estado de kioscos
        kiosks_status_response = client.get(
            '/api/v1/kiosks/status',
            headers=auth_headers(admin_token)
        )
        
        assert kiosks_status_response.status_code == 200
        assert isinstance(kiosks_status_response.json, list)
        
        # Verificar que nuestro kiosco creado aparece en la lista
        kiosk_found = False
        for kiosk in kiosks_status_response.json:
            if kiosk['id'] == kiosk_id:
                kiosk_found = True
                assert kiosk['name'] == 'Kiosco Estadísticas'
                assert kiosk['is_active'] == True
        
        assert kiosk_found, "El kiosco creado no se encontró en la lista de estado de kioscos"
    
    def test_kiosk_event_flow(self, client, admin_token, auth_headers):
        """
        Prueba del flujo de eventos para kioscos:
        1. Crear varios eventos
        2. Crear un kiosco con configuración específica
        3. Verificar que el kiosco muestra solo los eventos configurados
        """
        # 1. Crear varios eventos
        events = []
        for i in range(3):
            event_data = {
                'title': f'Evento Kiosco {i+1}',
                'description': f'Descripción del evento {i+1} para kiosco',
                'start_date': (datetime.utcnow() + timedelta(days=3+i)).isoformat(),
                'end_date': (datetime.utcnow() + timedelta(days=3+i, hours=8)).isoformat(),
                'location': f'Ubicación {i+1}',
                'is_active': True
            }
            
            event_response = client.post(
                '/api/v1/events/',
                json=event_data,
                headers=auth_headers(admin_token)
            )
            
            assert event_response.status_code == 201
            events.append(event_response.json['id'])
        
        # 2. Crear un kiosco como administrador
        kiosk_data = {
            'name': 'Kiosco Filtro',
            'location': 'Ubicación del kiosco filtrado',
            'is_active': True
        }
        
        kiosk_response = client.post(
            '/api/v1/kiosks/',
            json=kiosk_data,
            headers=auth_headers(admin_token)
        )
        
        assert kiosk_response.status_code == 201
        kiosk_id = kiosk_response.json['id']
        
        # Configurar el kiosco para mostrar solo el primer y tercer evento
        config_data = {
            'kiosk_id': kiosk_id,
            'language': 'es',
            'idle_timeout': 60,
            'event_filter': f'{events[0]},{events[2]}'
        }
        
        config_response = client.put(
            f'/api/v1/kiosks/{kiosk_id}/config',
            json=config_data,
            headers=auth_headers(admin_token)
        )
        
        assert config_response.status_code == 200
        
        # 3. Verificar que el kiosco muestra solo los eventos configurados
        events_response = client.get(f'/api/v1/kiosks/{kiosk_id}/events')
        
        assert events_response.status_code == 200
        assert isinstance(events_response.json, list)
        assert len(events_response.json) == 2
        
        event_ids = [e['id'] for e in events_response.json]
        assert events[0] in event_ids
        assert events[2] in event_ids
        assert events[1] not in event_ids 