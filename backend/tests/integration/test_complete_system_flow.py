"""
Pruebas de integración para evaluar el flujo completo del sistema
"""
import pytest
from datetime import datetime, timedelta
import json

class TestCompleteSystemFlow:
    """
    Pruebas de integración para evaluar el sistema completo,
    incluyendo la interacción entre todos los componentes: 
    usuarios, eventos, visitantes y kioscos.
    """
    
    def test_complete_event_registration_report_flow(self, client, admin_token, staff_token, auth_headers):
        """
        Prueba del flujo completo del sistema:
        1. Creación de usuarios con roles diferentes
        2. Creación de eventos y configuración
        3. Creación y configuración de kioscos
        4. Registro de visitantes
        5. Check-in de visitantes por kioscos
        6. Generación de reportes y estadísticas
        """
        # 1. Creación de un nuevo usuario con rol de reportes
        report_user_data = {
            'username': 'reporter',
            'password': 'Reporter123!',
            'email': 'reporter@test.com',
            'first_name': 'Usuario',
            'last_name': 'Reportes',
            'role': 'staff',
            'is_active': True
        }
        
        new_user_response = client.post(
            '/api/v1/users/',
            json=report_user_data,
            headers=auth_headers(admin_token)
        )
        
        assert new_user_response.status_code == 201
        report_user_id = new_user_response.json['id']
        
        # 2. Creación de un nuevo evento especial
        event_data = {
            'title': 'Exhibición Cultural',
            'description': 'Gran exhibición cultural anual',
            'start_date': (datetime.utcnow() + timedelta(days=7)).isoformat(),
            'end_date': (datetime.utcnow() + timedelta(days=14)).isoformat(),
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
        
        # 3. Crear dos kioscos para el evento
        kiosks = []
        for i in range(2):
            kiosk_data = {
                'name': f'Kiosco Exhibición {i+1}',
                'location': f'Entrada {i+1}',
                'is_active': True
            }
            
            kiosk_response = client.post(
                '/api/v1/kiosks/',
                json=kiosk_data,
                headers=auth_headers(admin_token)
            )
            
            assert kiosk_response.status_code == 201
            kiosks.append(kiosk_response.json['id'])
            
            # Configurar cada kiosco
            config_data = {
                'kiosk_id': kiosks[i],
                'language': 'es',
                'idle_timeout': 60,
                'event_filter': f'{event_id}'
            }
            
            config_response = client.put(
                f'/api/v1/kiosks/{kiosks[i]}/config',
                json=config_data,
                headers=auth_headers(admin_token)
            )
            
            assert config_response.status_code == 200
        
        # 4. Registrar múltiples visitantes para el evento
        visitors = []
        visitor_data_list = [
            {
                'name': 'Juan Pérez',
                'email': 'juan@test.com',
                'phone': '+1234567801',
                'event_id': event_id,
                'kiosk_id': kiosks[0]
            },
            {
                'name': 'María González',
                'email': 'maria@test.com',
                'phone': '+1234567802',
                'event_id': event_id,
                'kiosk_id': kiosks[0]
            },
            {
                'name': 'Roberto Sánchez',
                'email': 'roberto@test.com',
                'phone': '+1234567803',
                'event_id': event_id,
                'kiosk_id': kiosks[1]
            },
            {
                'name': 'Ana Rodríguez',
                'email': 'ana@test.com',
                'phone': '+1234567804',
                'event_id': event_id,
                'kiosk_id': kiosks[1]
            },
            {
                'name': 'Carlos Martínez',
                'email': 'carlos@test.com',
                'phone': '+1234567805',
                'event_id': event_id,
                'kiosk_id': kiosks[0]
            }
        ]
        
        for visitor_data in visitor_data_list:
            registration_response = client.post(
                '/api/v1/visitors/register',
                json=visitor_data
            )
            
            assert registration_response.status_code == 201
            visitors.append(registration_response.json['visitor_id'])
        
        # 5. Check-in de visitantes
        # Simular que los visitantes llegan y hacen check-in
        for i, visitor_id in enumerate(visitors):
            # Alternar los kioscos para los check-ins
            kiosk_id = kiosks[i % 2]
            
            checkin_data = {
                'visitor_id': visitor_id,
                'kiosk_id': kiosk_id,
                'event_id': event_id
            }
            
            checkin_response = client.post(
                '/api/v1/visitors/check-in',
                json=checkin_data
            )
            
            assert checkin_response.status_code == 201
        
        # 6. Simulación de actividad de kioscos
        for kiosk_id in kiosks:
            heartbeat_data = {
                'kiosk_id': kiosk_id,
                'status': 'active',
                'version': '1.0.0'
            }
            
            heartbeat_response = client.post(
                f'/api/v1/kiosks/{kiosk_id}/heartbeat',
                json=heartbeat_data
            )
            
            assert heartbeat_response.status_code == 200
        
        # 7. Verificación de estadísticas y reportes
        # Obtener estadísticas de visitantes
        stats_response = client.get(
            '/api/v1/visitors/stats',
            headers=auth_headers(admin_token)
        )
        
        assert stats_response.status_code == 200
        assert stats_response.json['total_visitors'] >= 5
        assert stats_response.json['total_check_ins'] >= 5
        
        # Obtener estadísticas de evento específico
        event_stats_response = client.get(
            f'/api/v1/events/{event_id}/stats',
            headers=auth_headers(admin_token)
        )
        
        assert event_stats_response.status_code == 200
        assert event_stats_response.json['registered_visitors'] >= 5
        assert event_stats_response.json['checked_in_visitors'] >= 5
        
        # Verificar que el staff puede ver el reporte de visitantes del evento
        staff_event_visitors_response = client.get(
            f'/api/v1/visitors/event/{event_id}',
            headers=auth_headers(staff_token)
        )
        
        assert staff_event_visitors_response.status_code == 200
        assert len(staff_event_visitors_response.json) >= 5
        
        # Verificar el estado de los kioscos
        kiosks_status_response = client.get(
            '/api/v1/kiosks/status',
            headers=auth_headers(admin_token)
        )
        
        assert kiosks_status_response.status_code == 200
        assert len(kiosks_status_response.json) >= 2
        
        # 8. Exportar datos para análisis (si el endpoint existe)
        export_response = client.get(
            f'/api/v1/events/{event_id}/export',
            headers=auth_headers(admin_token)
        )
        
        # Si el endpoint de exportación existe, verificar que funciona correctamente
        if export_response.status_code == 200:
            assert 'data' in export_response.json
            assert len(export_response.json['data']) >= 5
    
    def test_error_handling_and_edge_cases(self, client, admin_token, auth_headers):
        """
        Prueba de manejo de errores y casos extremos:
        1. Intentar crear entidades con datos incorrectos
        2. Intentar acciones no autorizadas
        3. Intentar manejar eventos no existentes
        4. Verificar la respuesta del sistema a solicitudes inválidas
        """
        # 1. Crear un evento con datos mínimos
        event_data = {
            'title': 'Evento Mínimo',
            'start_date': (datetime.utcnow() + timedelta(days=1)).isoformat(),
            'end_date': (datetime.utcnow() + timedelta(days=2)).isoformat(),
        }
        
        event_response = client.post(
            '/api/v1/events/',
            json=event_data,
            headers=auth_headers(admin_token)
        )
        
        assert event_response.status_code == 201
        event_id = event_response.json['id']
        
        # 2. Intentar crear un kiosco con datos incorrectos
        invalid_kiosk_data = {
            # Sin nombre, que debería ser obligatorio
            'location': 'Ubicación sin nombre',
            'is_active': True
        }
        
        invalid_kiosk_response = client.post(
            '/api/v1/kiosks/',
            json=invalid_kiosk_data,
            headers=auth_headers(admin_token)
        )
        
        assert invalid_kiosk_response.status_code == 400
        
        # 3. Intentar acceder a un evento que no existe
        nonexistent_event_response = client.get(
            '/api/v1/events/999999',
            headers=auth_headers(admin_token)
        )
        
        assert nonexistent_event_response.status_code == 404
        
        # 4. Intentar registrar un visitante sin evento
        invalid_visitor_data = {
            'name': 'Visitante Sin Evento',
            'email': 'visitante.sin.evento@test.com',
            'phone': '+1234567899'
            # Sin event_id
        }
        
        invalid_visitor_response = client.post(
            '/api/v1/visitors/',
            json=invalid_visitor_data,
            headers=auth_headers(admin_token)
        )
        
        assert invalid_visitor_response.status_code == 400
        
        # 5. Intentar hacer check-in de un visitante que no existe
        invalid_checkin_data = {
            'visitor_id': 999999,
            'event_id': event_id
        }
        
        invalid_checkin_response = client.post(
            '/api/v1/visitors/check-in',
            json=invalid_checkin_data
        )
        
        assert invalid_checkin_response.status_code == 404
        
        # 6. Intentar acceder sin autenticación a un endpoint protegido
        no_auth_response = client.get('/api/v1/users/')
        
        assert no_auth_response.status_code == 401
        
        # 7. Verificar que la API maneja correctamente los métodos HTTP no permitidos
        method_not_allowed_response = client.delete('/api/v1/auth/login')
        
        assert method_not_allowed_response.status_code == 405
        
        # 8. Verificar el manejo de solicitudes mal formadas
        malformed_json_response = client.post(
            '/api/v1/auth/login',
            data="esto no es un JSON válido",
            headers={'Content-Type': 'application/json'}
        )
        
        assert malformed_json_response.status_code == 400 