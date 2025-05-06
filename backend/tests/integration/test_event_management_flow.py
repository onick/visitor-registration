"""
Pruebas de integración para el flujo de gestión de eventos
"""
import pytest
from datetime import datetime, timedelta

class TestEventManagementFlow:
    """
    Pruebas de integración para el flujo completo de gestión de eventos
    """
    
    def test_event_creation_visitor_flow(self, client, admin_token, staff_token, auth_headers):
        """
        Prueba del flujo de creación de evento y registro de visitantes:
        1. Crear un evento como administrador
        2. Verificar que el personal puede ver el evento
        3. Registrar varios visitantes para el evento
        4. Verificar que los visitantes aparecen en la lista del evento
        """
        # 1. Crear un evento como administrador
        event_data = {
            'title': 'Exposición de Arte Contemporáneo',
            'description': 'Exposición de artistas locales',
            'start_date': (datetime.utcnow() + timedelta(days=5)).isoformat(),
            'end_date': (datetime.utcnow() + timedelta(days=15)).isoformat(),
            'location': 'Sala Principal',
            'is_active': True
        }
        
        event_response = client.post(
            '/api/v1/events/',
            json=event_data,
            headers=auth_headers(admin_token)
        )
        
        assert event_response.status_code == 201
        event_id = event_response.json['id']
        
        # 2. Verificar que el personal puede ver el evento
        staff_events_response = client.get(
            '/api/v1/events/',
            headers=auth_headers(staff_token)
        )
        
        assert staff_events_response.status_code == 200
        assert isinstance(staff_events_response.json, list)
        
        event_found = False
        for event in staff_events_response.json:
            if event['id'] == event_id:
                event_found = True
                assert event['title'] == 'Exposición de Arte Contemporáneo'
                assert event['location'] == 'Sala Principal'
        
        assert event_found, "El evento creado no se encontró en la lista visible para el personal"
        
        # 3. Registrar varios visitantes para el evento
        visitors_data = [
            {
                'name': 'Carlos Pérez',
                'email': 'carlos@example.com',
                'phone': '+1234567890'
            },
            {
                'name': 'Laura Gómez',
                'email': 'laura@example.com',
                'phone': '+1234567891'
            },
            {
                'name': 'Miguel Rodríguez',
                'email': 'miguel@example.com',
                'phone': '+1234567892'
            }
        ]
        
        registered_visitor_ids = []
        for visitor_data in visitors_data:
            visitor_data['event_id'] = event_id
            
            registration_response = client.post(
                '/api/v1/visitors/',
                json=visitor_data,
                headers=auth_headers(staff_token)
            )
            
            assert registration_response.status_code == 201
            registered_visitor_ids.append(registration_response.json['id'])
        
        # 4. Verificar que los visitantes aparecen en la lista del evento
        event_visitors_response = client.get(
            f'/api/v1/visitors/event/{event_id}',
            headers=auth_headers(admin_token)
        )
        
        assert event_visitors_response.status_code == 200
        assert isinstance(event_visitors_response.json, list)
        assert len(event_visitors_response.json) >= 3
        
        # Verificar que los visitantes registrados están en la lista
        for visitor_id in registered_visitor_ids:
            visitor_found = False
            for visitor in event_visitors_response.json:
                if visitor['id'] == visitor_id:
                    visitor_found = True
                    break
            assert visitor_found, f"El visitante con ID {visitor_id} no se encontró en la lista del evento"
    
    def test_event_update_cancel_flow(self, client, admin_token, auth_headers):
        """
        Prueba del flujo de actualización y cancelación de eventos:
        1. Crear un evento como administrador
        2. Actualizar detalles del evento
        3. Cancelar el evento 
        4. Verificar que el evento ya no está activo
        """
        # 1. Crear un evento como administrador
        event_data = {
            'title': 'Conferencia sobre Historia',
            'description': 'Conferencia sobre la historia del país',
            'start_date': (datetime.utcnow() + timedelta(days=10)).isoformat(),
            'end_date': (datetime.utcnow() + timedelta(days=10, hours=4)).isoformat(),
            'location': 'Auditorio',
            'is_active': True
        }
        
        event_response = client.post(
            '/api/v1/events/',
            json=event_data,
            headers=auth_headers(admin_token)
        )
        
        assert event_response.status_code == 201
        event_id = event_response.json['id']
        
        # 2. Actualizar detalles del evento
        update_data = {
            'title': 'Conferencia sobre Historia Nacional',
            'description': 'Conferencia sobre la historia nacional y sus personajes',
            'location': 'Auditorio Principal'
        }
        
        update_response = client.put(
            f'/api/v1/events/{event_id}',
            json=update_data,
            headers=auth_headers(admin_token)
        )
        
        assert update_response.status_code == 200
        assert update_response.json['title'] == 'Conferencia sobre Historia Nacional'
        assert update_response.json['location'] == 'Auditorio Principal'
        
        # 3. Cancelar el evento
        cancel_data = {
            'is_active': False
        }
        
        cancel_response = client.put(
            f'/api/v1/events/{event_id}',
            json=cancel_data,
            headers=auth_headers(admin_token)
        )
        
        assert cancel_response.status_code == 200
        assert cancel_response.json['is_active'] == False
        
        # 4. Verificar que el evento ya no está activo
        event_response = client.get(
            f'/api/v1/events/{event_id}',
            headers=auth_headers(admin_token)
        )
        
        assert event_response.status_code == 200
        assert event_response.json['is_active'] == False
    
    def test_search_filter_events_flow(self, client, admin_token, auth_headers):
        """
        Prueba del flujo de búsqueda y filtrado de eventos:
        1. Crear varios eventos con diferentes fechas y estados
        2. Buscar eventos por título
        3. Filtrar eventos por estado (activo/inactivo)
        4. Filtrar eventos por fecha
        """
        # 1. Crear varios eventos con diferentes fechas y estados
        events_data = [
            {
                'title': 'Exposición de Fotografía',
                'description': 'Exposición de fotografía contemporánea',
                'start_date': (datetime.utcnow() + timedelta(days=2)).isoformat(),
                'end_date': (datetime.utcnow() + timedelta(days=12)).isoformat(),
                'location': 'Galería Este',
                'is_active': True
            },
            {
                'title': 'Taller de Pintura',
                'description': 'Taller de pintura para principiantes',
                'start_date': (datetime.utcnow() + timedelta(days=15)).isoformat(),
                'end_date': (datetime.utcnow() + timedelta(days=15, hours=6)).isoformat(),
                'location': 'Sala de Talleres',
                'is_active': True
            },
            {
                'title': 'Concierto de Música Clásica',
                'description': 'Concierto de música clásica con la orquesta nacional',
                'start_date': (datetime.utcnow() + timedelta(days=5)).isoformat(),
                'end_date': (datetime.utcnow() + timedelta(days=5, hours=3)).isoformat(),
                'location': 'Auditorio Principal',
                'is_active': False
            }
        ]
        
        created_events = []
        for event_data in events_data:
            event_response = client.post(
                '/api/v1/events/',
                json=event_data,
                headers=auth_headers(admin_token)
            )
            
            assert event_response.status_code == 201
            created_events.append(event_response.json)
        
        # 2. Buscar eventos por título
        search_response = client.get(
            '/api/v1/events/?search=pintura',
            headers=auth_headers(admin_token)
        )
        
        assert search_response.status_code == 200
        assert isinstance(search_response.json, list)
        assert len(search_response.json) >= 1
        
        found_taller = False
        for event in search_response.json:
            if 'Taller de Pintura' in event['title']:
                found_taller = True
                break
        
        assert found_taller, "No se encontró el evento 'Taller de Pintura' en la búsqueda"
        
        # 3. Filtrar eventos por estado (activo/inactivo)
        inactive_response = client.get(
            '/api/v1/events/?active=false',
            headers=auth_headers(admin_token)
        )
        
        assert inactive_response.status_code == 200
        assert isinstance(inactive_response.json, list)
        
        found_concert = False
        for event in inactive_response.json:
            if 'Concierto de Música Clásica' in event['title']:
                found_concert = True
                assert event['is_active'] == False
                break
        
        assert found_concert, "No se encontró el evento inactivo 'Concierto de Música Clásica' en el filtrado"
        
        # 4. Filtrar eventos por fecha
        future_date = (datetime.utcnow() + timedelta(days=10)).strftime('%Y-%m-%d')
        date_filter_response = client.get(
            f'/api/v1/events/?date={future_date}',
            headers=auth_headers(admin_token)
        )
        
        assert date_filter_response.status_code == 200
        assert isinstance(date_filter_response.json, list)
        
        # Verificar que solo muestra eventos que ocurren en o después de la fecha especificada
        for event in date_filter_response.json:
            event_start = datetime.fromisoformat(event['start_date'].replace('Z', '+00:00'))
            event_end = datetime.fromisoformat(event['end_date'].replace('Z', '+00:00'))
            filter_date = datetime.strptime(future_date, '%Y-%m-%d')
            
            assert event_end >= filter_date, f"El evento {event['title']} termina antes de la fecha de filtro" 