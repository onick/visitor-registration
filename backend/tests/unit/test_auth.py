"""
Pruebas para los endpoints de autenticación
"""
import pytest
from flask import json

class TestAuth:
    """
    Pruebas para la autenticación de usuarios
    """
    
    def test_login_success(self, client, create_admin):
        """
        Prueba de inicio de sesión exitoso
        """
        response = client.post('/api/v1/auth/login', json={
            'email': 'admin@test.com',
            'password': 'Admin123!'
        })
        
        assert response.status_code == 200
        assert 'access_token' in response.json
        assert 'refresh_token' in response.json
        assert 'user' in response.json
        assert response.json['user']['email'] == 'admin@test.com'
        assert response.json['user']['role'] == 'admin'
    
    def test_login_invalid_credentials(self, client, create_admin):
        """
        Prueba de inicio de sesión con credenciales inválidas
        """
        response = client.post('/api/v1/auth/login', json={
            'email': 'admin@test.com',
            'password': 'WrongPassword123!'
        })
        
        assert response.status_code == 401
        assert 'error' in response.json
    
    def test_login_missing_fields(self, client):
        """
        Prueba de inicio de sesión con campos faltantes
        """
        response = client.post('/api/v1/auth/login', json={
            'email': 'admin@test.com'
        })
        
        assert response.status_code == 400
        assert 'error' in response.json
    
    def test_register_user_as_admin(self, client, admin_token, auth_headers):
        """
        Prueba de registro de usuario como administrador
        """
        response = client.post(
            '/api/v1/auth/register', 
            json={
                'email': 'new-staff@test.com',
                'password': 'NewStaff123!',
                'name': 'New Staff',
                'role': 'staff'
            },
            headers=auth_headers(admin_token)
        )
        
        assert response.status_code == 201
        assert response.json['email'] == 'new-staff@test.com'
        assert response.json['role'] == 'staff'
    
    def test_register_user_without_auth(self, client):
        """
        Prueba de registro de usuario sin autenticación
        """
        response = client.post('/api/v1/auth/register', json={
            'email': 'new-staff@test.com',
            'password': 'NewStaff123!',
            'name': 'New Staff',
            'role': 'staff'
        })
        
        assert response.status_code == 401
    
    def test_register_user_as_staff(self, client, staff_token, auth_headers):
        """
        Prueba de registro de usuario como staff (no debería tener permisos)
        """
        response = client.post(
            '/api/v1/auth/register', 
            json={
                'email': 'new-staff2@test.com',
                'password': 'NewStaff123!',
                'name': 'New Staff 2',
                'role': 'staff'
            },
            headers=auth_headers(staff_token)
        )
        
        assert response.status_code == 403
    
    def test_get_user_info(self, client, admin_token, auth_headers, create_admin):
        """
        Prueba para obtener información del usuario actual
        """
        response = client.get(
            '/api/v1/auth/me',
            headers=auth_headers(admin_token)
        )
        
        assert response.status_code == 200
        assert 'email' in response.json
        assert response.json['role'] == 'admin'
    
    def test_get_user_info_without_auth(self, client):
        """
        Prueba para obtener información del usuario sin autenticación
        """
        response = client.get('/api/v1/auth/me')
        
        assert response.status_code == 401
    
    def test_change_password(self, client, admin_token, auth_headers, create_admin):
        """
        Prueba para cambiar contraseña
        """
        response = client.post(
            '/api/v1/auth/change-password',
            json={
                'current_password': 'Admin123!',
                'new_password': 'NewAdmin123!'
            },
            headers=auth_headers(admin_token)
        )
        
        assert response.status_code == 200
        assert 'message' in response.json
        
        # Verificar que puede iniciar sesión con la nueva contraseña
        response = client.post('/api/v1/auth/login', json={
            'email': 'admin@test.com',
            'password': 'NewAdmin123!'
        })
        
        assert response.status_code == 200
        assert 'access_token' in response.json
    
    def test_change_password_wrong_current(self, client, admin_token, auth_headers):
        """
        Prueba para cambiar contraseña con contraseña actual incorrecta
        """
        response = client.post(
            '/api/v1/auth/change-password',
            json={
                'current_password': 'WrongAdmin123!',
                'new_password': 'NewAdmin123!'
            },
            headers=auth_headers(admin_token)
        )
        
        assert response.status_code == 400
        assert 'error' in response.json 