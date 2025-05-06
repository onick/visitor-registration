"""
Pruebas para los endpoints de eventos
"""
import pytest
from datetime import datetime, timedelta

class TestEvents:
    """
    Pruebas para los endpoints de eventos
    """
    
    def test_get_events_public(self, client):
        """
        Prueba para obtener lista de eventos (acceso público)
        """
        response = client.get('/api/v1/events/')
        
        assert response.status_code == 200
        assert isinstance(response.json, list)
    
    def test_get_event_by_id(self, client, create_event):
        """
        Prueba para obtener un evento por su ID
        """
        event_id = create_event
        response = client.get(f'/api/v1/events/{event_id}')
        
        assert response.status_code == 200
        assert response.json['id'] == event_id
        assert response.json['title'] == 'Evento de prueba'
    
    def test_get_nonexistent_event(self, client):
        """
        Prueba para obtener un evento que no existe
        """
        response = client.get('/api/v1/events/999')
        
        assert response.status_code == 404
    
    def test_create_event_admin(self, client, admin_token, auth_headers):
        """
        Prueba para crear un evento como administrador
        """
        event_data = {
            'title': 'Nuevo Evento',
            'description': 'Descripción del nuevo evento',
            'start_date': (datetime.utcnow() + timedelta(days=1)).isoformat(),
            'end_date': (datetime.utcnow() + timedelta(days=1, hours=8)).isoformat(),
            'location': 'Ubicación del evento',
            'is_active': True
        }
        
        response = client.post(
            '/api/v1/events/',
            json=event_data,
            headers=auth_headers(admin_token)
        )
        
        assert response.status_code == 201
        assert response.json['title'] == 'Nuevo Evento'
        assert 'id' in response.json
    
    def test_create_event_staff(self, client, staff_token, auth_headers):
        """
        Prueba para crear un evento como staff
        """
        event_data = {
            'title': 'Evento Staff',
            'description': 'Descripción del evento creado por staff',
            'start_date': (datetime.utcnow() + timedelta(days=2)).isoformat(),
            'end_date': (datetime.utcnow() + timedelta(days=2, hours=6)).isoformat(),
            'location': 'Ubicación del evento staff',
            'is_active': True
        }
        
        response = client.post(
            '/api/v1/events/',
            json=event_data,
            headers=auth_headers(staff_token)
        )
        
        assert response.status_code == 201
        assert response.json['title'] == 'Evento Staff'
    
    def test_create_event_no_auth(self, client):
        """
        Prueba para crear un evento sin autenticación
        """
        event_data = {
            'title': 'Evento Sin Auth',
            'description': 'Descripción del evento sin auth',
            'start_date': (datetime.utcnow() + timedelta(days=3)).isoformat(),
            'end_date': (datetime.utcnow() + timedelta(days=3, hours=4)).isoformat(),
            'location': 'Ubicación sin auth',
            'is_active': True
        }
        
        response = client.post('/api/v1/events/', json=event_data)
        
        assert response.status_code == 401
    
    def test_create_event_missing_fields(self, client, admin_token, auth_headers):
        """
        Prueba para crear un evento con campos faltantes
        """
        event_data = {
            'title': 'Evento Incompleto',
            'description': 'Descripción del evento incompleto'
            # Faltan campos obligatorios
        }
        
        response = client.post(
            '/api/v1/events/',
            json=event_data,
            headers=auth_headers(admin_token)
        )
        
        assert response.status_code == 400
        assert 'error' in response.json
    
    def test_update_event(self, client, create_event, admin_token, auth_headers):
        """
        Prueba para actualizar un evento
        """
        event_id = create_event
        update_data = {
            'title': 'Evento Actualizado',
            'description': 'Descripción actualizada'
        }
        
        response = client.put(
            f'/api/v1/events/{event_id}',
            json=update_data,
            headers=auth_headers(admin_token)
        )
        
        assert response.status_code == 200
        assert response.json['title'] == 'Evento Actualizado'
        assert response.json['description'] == 'Descripción actualizada'
    
    def test_delete_event_admin(self, client, create_event, admin_token, auth_headers):
        """
        Prueba para eliminar un evento como administrador
        """
        event_id = create_event
        
        response = client.delete(
            f'/api/v1/events/{event_id}',
            headers=auth_headers(admin_token)
        )
        
        assert response.status_code == 204
        
        # Verificar que el evento ya no existe
        response = client.get(f'/api/v1/events/{event_id}')
        assert response.status_code == 404
    
    def test_delete_event_staff(self, client, create_event, staff_token, auth_headers):
        """
        Prueba para eliminar un evento como staff (no debería tener permisos)
        """
        event_id = create_event
        
        response = client.delete(
            f'/api/v1/events/{event_id}',
            headers=auth_headers(staff_token)
        )
        
        assert response.status_code == 403
    
    def test_get_active_events(self, client, create_event):
        """
        Prueba para obtener eventos activos
        """
        response = client.get('/api/v1/events/active')
        
        assert response.status_code == 200
        assert isinstance(response.json, list)
        
        # Si hemos creado un evento activo, debería haber al menos uno
        if create_event:
            assert len(response.json) >= 1
    
    def test_search_events(self, client, create_event):
        """
        Prueba para buscar eventos
        """
        # Crear el evento primero
        event_id = create_event
        
        # Buscar por parte del título
        response = client.get('/api/v1/events/search?q=prueba')
        
        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) >= 1
        
        # Si buscamos algo que no existe, debería devolver lista vacía
        response = client.get('/api/v1/events/search?q=noexiste123456')
        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) == 0 