"""
Pruebas para los endpoints de visitantes
"""
import pytest

class TestVisitors:
    """
    Pruebas para los endpoints de visitantes
    """
    
    def test_get_visitors_list_admin(self, client, create_visitor, admin_token, auth_headers):
        """
        Prueba para obtener lista de visitantes como administrador
        """
        response = client.get(
            '/api/v1/visitors/',
            headers=auth_headers(admin_token)
        )
        
        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) >= 1
    
    def test_get_visitors_list_staff(self, client, create_visitor, staff_token, auth_headers):
        """
        Prueba para obtener lista de visitantes como staff
        """
        response = client.get(
            '/api/v1/visitors/',
            headers=auth_headers(staff_token)
        )
        
        assert response.status_code == 200
        assert isinstance(response.json, list)
    
    def test_get_visitors_list_no_auth(self, client):
        """
        Prueba para obtener lista de visitantes sin autenticación
        """
        response = client.get('/api/v1/visitors/')
        
        assert response.status_code == 401
    
    def test_create_visitor_admin(self, client, admin_token, auth_headers):
        """
        Prueba para crear un visitante como administrador
        """
        visitor_data = {
            'name': 'Nuevo Visitante',
            'email': 'nuevo@visitante.com',
            'phone': '+1234567891'
        }
        
        response = client.post(
            '/api/v1/visitors/',
            json=visitor_data,
            headers=auth_headers(admin_token)
        )
        
        assert response.status_code == 201
        assert response.json['name'] == 'Nuevo Visitante'
        assert response.json['email'] == 'nuevo@visitante.com'
    
    def test_create_visitor_staff(self, client, staff_token, auth_headers):
        """
        Prueba para crear un visitante como staff
        """
        visitor_data = {
            'name': 'Visitante Staff',
            'email': 'visitante.staff@test.com',
            'phone': '+1234567892'
        }
        
        response = client.post(
            '/api/v1/visitors/',
            json=visitor_data,
            headers=auth_headers(staff_token)
        )
        
        assert response.status_code == 201
        assert response.json['name'] == 'Visitante Staff'
    
    def test_create_visitor_no_auth(self, client):
        """
        Prueba para crear un visitante sin autenticación
        """
        visitor_data = {
            'name': 'Visitante Sin Auth',
            'email': 'visitante.noauth@test.com',
            'phone': '+1234567893'
        }
        
        response = client.post('/api/v1/visitors/', json=visitor_data)
        
        assert response.status_code == 401
    
    def test_get_visitor_by_id(self, client, create_visitor, admin_token, auth_headers):
        """
        Prueba para obtener un visitante por su ID
        """
        visitor_id = create_visitor
        
        response = client.get(
            f'/api/v1/visitors/{visitor_id}',
            headers=auth_headers(admin_token)
        )
        
        assert response.status_code == 200
        assert response.json['id'] == visitor_id
        assert response.json['name'] == 'Visitante Prueba'
    
    def test_update_visitor(self, client, create_visitor, admin_token, auth_headers):
        """
        Prueba para actualizar un visitante
        """
        visitor_id = create_visitor
        update_data = {
            'name': 'Visitante Actualizado',
            'email': 'actualizado@test.com'
        }
        
        response = client.put(
            f'/api/v1/visitors/{visitor_id}',
            json=update_data,
            headers=auth_headers(admin_token)
        )
        
        assert response.status_code == 200
        assert response.json['name'] == 'Visitante Actualizado'
        assert response.json['email'] == 'actualizado@test.com'
    
    def test_delete_visitor(self, client, create_visitor, admin_token, auth_headers):
        """
        Prueba para eliminar un visitante
        """
        visitor_id = create_visitor
        
        response = client.delete(
            f'/api/v1/visitors/{visitor_id}',
            headers=auth_headers(admin_token)
        )
        
        assert response.status_code == 204
        
        # Verificar que el visitante ya no existe
        response = client.get(
            f'/api/v1/visitors/{visitor_id}',
            headers=auth_headers(admin_token)
        )
        assert response.status_code == 404
    
    def test_delete_visitor_staff(self, client, create_visitor, staff_token, auth_headers):
        """
        Prueba para eliminar un visitante como staff (no debería tener permisos)
        """
        visitor_id = create_visitor
        
        response = client.delete(
            f'/api/v1/visitors/{visitor_id}',
            headers=auth_headers(staff_token)
        )
        
        assert response.status_code == 403
    
    def test_register_visitor_event(self, client, create_event, create_kiosk):
        """
        Prueba para registrar un visitante en un evento (operación combinada)
        """
        registration_data = {
            'name': 'Visitante Registro',
            'email': 'registro@test.com',
            'phone': '+1234567894',
            'event_id': create_event,
            'kiosk_id': create_kiosk
        }
        
        response = client.post('/api/v1/visitors/register', json=registration_data)
        
        assert response.status_code == 201
        assert 'message' in response.json
        assert 'visitor_id' in response.json
        assert 'event_id' in response.json
        assert 'check_in_id' in response.json
    
    def test_get_event_visitors(self, client, create_event, create_visitor, admin_token, auth_headers):
        """
        Prueba para obtener visitantes de un evento
        """
        # Primero registramos un visitante en el evento
        registration_data = {
            'visitor_id': create_visitor,
            'event_id': create_event,
            'kiosk_id': create_kiosk
        }
        
        client.post('/api/v1/visitors/check-in', json=registration_data)
        
        response = client.get(
            f'/api/v1/visitors/event/{create_event}',
            headers=auth_headers(admin_token)
        )
        
        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) >= 1
    
    def test_visitor_check_in(self, client, create_visitor, create_event, create_kiosk):
        """
        Prueba para registrar la asistencia de un visitante a un evento
        """
        check_in_data = {
            'visitor_id': create_visitor,
            'event_id': create_event,
            'kiosk_id': create_kiosk
        }
        
        response = client.post('/api/v1/visitors/check-in', json=check_in_data)
        
        assert response.status_code == 201
        assert 'message' in response.json
    
    def test_duplicate_check_in(self, client, create_visitor, create_event, create_kiosk):
        """
        Prueba para registrar la asistencia de un visitante que ya está registrado
        """
        check_in_data = {
            'visitor_id': create_visitor,
            'event_id': create_event,
            'kiosk_id': create_kiosk
        }
        
        # Primer registro debería ser exitoso
        response = client.post('/api/v1/visitors/check-in', json=check_in_data)
        assert response.status_code == 201
        
        # Segundo registro debería fallar por duplicado
        response = client.post('/api/v1/visitors/check-in', json=check_in_data)
        assert response.status_code == 409
    
    def test_visitor_stats(self, client, create_visitor, create_event, create_kiosk, admin_token, auth_headers):
        """
        Prueba para obtener estadísticas de visitantes
        """
        # Registramos un visitante para generar estadísticas
        check_in_data = {
            'visitor_id': create_visitor,
            'event_id': create_event,
            'kiosk_id': create_kiosk
        }
        
        client.post('/api/v1/visitors/check-in', json=check_in_data)
        
        response = client.get(
            '/api/v1/visitors/stats',
            headers=auth_headers(admin_token)
        )
        
        assert response.status_code == 200
        assert 'total_visitors' in response.json
        assert 'total_check_ins' in response.json
        assert 'visitors_today' in response.json
        assert 'check_ins_today' in response.json 