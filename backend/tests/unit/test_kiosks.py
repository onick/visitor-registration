"""
Pruebas para los endpoints de kioscos
"""
import pytest
from datetime import datetime, timedelta

class TestKiosks:
    """
    Pruebas para los endpoints de kioscos
    """
    
    def test_get_kiosks_list_admin(self, client, create_kiosk, admin_token, auth_headers):
        """
        Prueba para obtener lista de kioscos como administrador
        """
        response = client.get(
            '/api/v1/kiosks/',
            headers=auth_headers(admin_token)
        )
        
        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) >= 1
    
    def test_get_kiosks_list_staff(self, client, create_kiosk, staff_token, auth_headers):
        """
        Prueba para obtener lista de kioscos como staff
        """
        response = client.get(
            '/api/v1/kiosks/',
            headers=auth_headers(staff_token)
        )
        
        assert response.status_code == 200
        assert isinstance(response.json, list)
    
    def test_get_kiosks_list_no_auth(self, client):
        """
        Prueba para obtener lista de kioscos sin autenticación
        """
        response = client.get('/api/v1/kiosks/')
        
        assert response.status_code == 401
    
    def test_create_kiosk_admin(self, client, admin_token, auth_headers):
        """
        Prueba para crear un kiosco como administrador
        """
        kiosk_data = {
            'name': 'Nuevo Kiosco',
            'location': 'Nueva Ubicación',
            'is_active': True
        }
        
        response = client.post(
            '/api/v1/kiosks/',
            json=kiosk_data,
            headers=auth_headers(admin_token)
        )
        
        assert response.status_code == 201
        assert response.json['name'] == 'Nuevo Kiosco'
        assert response.json['location'] == 'Nueva Ubicación'
    
    def test_create_kiosk_staff(self, client, staff_token, auth_headers):
        """
        Prueba para crear un kiosco como staff (no debería tener permisos)
        """
        kiosk_data = {
            'name': 'Kiosco Staff',
            'location': 'Ubicación Staff',
            'is_active': True
        }
        
        response = client.post(
            '/api/v1/kiosks/',
            json=kiosk_data,
            headers=auth_headers(staff_token)
        )
        
        assert response.status_code == 403
    
    def test_create_kiosk_missing_fields(self, client, admin_token, auth_headers):
        """
        Prueba para crear un kiosco con campos faltantes
        """
        kiosk_data = {
            'name': 'Kiosco Incompleto'
            # Falta el campo location
        }
        
        response = client.post(
            '/api/v1/kiosks/',
            json=kiosk_data,
            headers=auth_headers(admin_token)
        )
        
        assert response.status_code == 400
    
    def test_get_kiosk_by_id(self, client, create_kiosk):
        """
        Prueba para obtener un kiosco por su ID
        """
        kiosk_id = create_kiosk
        
        response = client.get(f'/api/v1/kiosks/{kiosk_id}')
        
        assert response.status_code == 200
        assert response.json['id'] == kiosk_id
        assert response.json['name'] == 'Kiosco Prueba'
    
    def test_update_kiosk_admin(self, client, create_kiosk, admin_token, auth_headers):
        """
        Prueba para actualizar un kiosco como administrador
        """
        kiosk_id = create_kiosk
        update_data = {
            'name': 'Kiosco Actualizado',
            'location': 'Ubicación Actualizada',
            'is_active': False
        }
        
        response = client.put(
            f'/api/v1/kiosks/{kiosk_id}',
            json=update_data,
            headers=auth_headers(admin_token)
        )
        
        assert response.status_code == 200
        assert response.json['name'] == 'Kiosco Actualizado'
        assert response.json['location'] == 'Ubicación Actualizada'
        assert response.json['is_active'] == False
    
    def test_update_kiosk_staff(self, client, create_kiosk, staff_token, auth_headers):
        """
        Prueba para actualizar un kiosco como staff (no debería tener permisos)
        """
        kiosk_id = create_kiosk
        update_data = {
            'name': 'Kiosco Staff Update',
            'location': 'Ubicación Staff Update'
        }
        
        response = client.put(
            f'/api/v1/kiosks/{kiosk_id}',
            json=update_data,
            headers=auth_headers(staff_token)
        )
        
        assert response.status_code == 403
    
    def test_delete_kiosk_admin(self, client, create_kiosk, admin_token, auth_headers):
        """
        Prueba para eliminar un kiosco como administrador
        """
        kiosk_id = create_kiosk
        
        response = client.delete(
            f'/api/v1/kiosks/{kiosk_id}',
            headers=auth_headers(admin_token)
        )
        
        assert response.status_code == 204
        
        # Verificar que el kiosco ya no existe
        response = client.get(f'/api/v1/kiosks/{kiosk_id}')
        assert response.status_code == 404
    
    def test_delete_kiosk_staff(self, client, create_kiosk, staff_token, auth_headers):
        """
        Prueba para eliminar un kiosco como staff (no debería tener permisos)
        """
        kiosk_id = create_kiosk
        
        response = client.delete(
            f'/api/v1/kiosks/{kiosk_id}',
            headers=auth_headers(staff_token)
        )
        
        assert response.status_code == 403
    
    def test_get_kiosk_config(self, client, create_kiosk):
        """
        Prueba para obtener la configuración de un kiosco
        """
        kiosk_id = create_kiosk
        
        response = client.get(f'/api/v1/kiosks/{kiosk_id}/config')
        
        assert response.status_code == 200
        assert response.json['kiosk_id'] == kiosk_id
        assert 'language' in response.json
        assert 'idle_timeout' in response.json
    
    def test_update_kiosk_config(self, client, create_kiosk, admin_token, auth_headers):
        """
        Prueba para actualizar la configuración de un kiosco
        """
        kiosk_id = create_kiosk
        config_data = {
            'kiosk_id': kiosk_id,
            'language': 'en',
            'idle_timeout': 120,
            'custom_message': 'Bienvenido al Centro Cultural'
        }
        
        response = client.put(
            f'/api/v1/kiosks/{kiosk_id}/config',
            json=config_data,
            headers=auth_headers(admin_token)
        )
        
        assert response.status_code == 200
        assert response.json['language'] == 'en'
        assert response.json['idle_timeout'] == 120
        assert response.json['custom_message'] == 'Bienvenido al Centro Cultural'
    
    def test_kiosk_heartbeat(self, client, create_kiosk):
        """
        Prueba para reportar actividad de un kiosco
        """
        kiosk_id = create_kiosk
        
        response = client.post(f'/api/v1/kiosks/{kiosk_id}/heartbeat')
        
        assert response.status_code == 200
        assert 'status' in response.json
        assert 'is_active' in response.json
    
    def test_get_kiosk_events(self, client, create_kiosk, create_event):
        """
        Prueba para obtener eventos relevantes para un kiosco
        """
        kiosk_id = create_kiosk
        
        response = client.get(f'/api/v1/kiosks/{kiosk_id}/events')
        
        assert response.status_code == 200
        assert isinstance(response.json, list)
        
        # Si hay un evento creado y activo, debería aparecer en la lista
        if create_event:
            assert len(response.json) >= 1
            assert 'id' in response.json[0]
            assert 'title' in response.json[0]
    
    def test_get_kiosks_status(self, client, create_kiosk, admin_token, auth_headers):
        """
        Prueba para obtener estado de todos los kioscos
        """
        response = client.get(
            '/api/v1/kiosks/status',
            headers=auth_headers(admin_token)
        )
        
        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) >= 1
        
        # Verificar que los campos necesarios estén presentes
        kiosk_info = response.json[0]
        assert 'id' in kiosk_info
        assert 'name' in kiosk_info
        assert 'location' in kiosk_info
        assert 'is_active' in kiosk_info
        assert 'is_online' in kiosk_info 