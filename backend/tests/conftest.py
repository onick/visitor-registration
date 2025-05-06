"""
Configuraciones y fixtures para las pruebas de la API de registro de visitantes
"""
import os
import pytest
import tempfile
from datetime import datetime, timedelta

from app import create_app
from app.models import db as _db
from app.models.user import User
from app.models.event import Event
from app.models.visitor import Visitor
from app.models.kiosk import Kiosk

@pytest.fixture(scope='session')
def app():
    """
    Crea una instancia de la aplicación Flask para las pruebas
    """
    # Configuración para testing
    db_fd, db_path = tempfile.mkstemp()
    
    config = {
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'TESTING': True,
        'JWT_SECRET_KEY': 'secret-key-for-testing',
        'JWT_ACCESS_TOKEN_EXPIRES': timedelta(hours=1),
        'JWT_REFRESH_TOKEN_EXPIRES': timedelta(days=30),
    }
    
    app = create_app(config)
    
    with app.app_context():
        _db.create_all()
        # Crear datos iniciales
        _setup_test_data(_db)
        
        yield app
    
    os.close(db_fd)
    os.unlink(db_path)

def _setup_test_data(db):
    """
    Configura datos iniciales para las pruebas
    """
    # Crear usuarios de prueba (admin y staff)
    admin = User(
        username='admin_test',
        email='admin@test.com',
        first_name='Admin',
        last_name='Test',
        role='admin',
        is_active=True
    )
    admin.set_password('admin_password')
    
    staff = User(
        username='staff_test',
        email='staff@test.com',
        first_name='Staff',
        last_name='Test',
        role='staff',
        is_active=True
    )
    staff.set_password('staff_password')
    
    # Crear algunos eventos de prueba
    event1 = Event(
        title='Evento de Prueba 1',
        description='Descripción del evento de prueba 1',
        start_date=datetime.utcnow() + timedelta(days=1),
        end_date=datetime.utcnow() + timedelta(days=2),
        location='Ubicación 1',
        is_active=True
    )
    
    event2 = Event(
        title='Evento de Prueba 2',
        description='Descripción del evento de prueba 2',
        start_date=datetime.utcnow() + timedelta(days=3),
        end_date=datetime.utcnow() + timedelta(days=4),
        location='Ubicación 2',
        is_active=True
    )
    
    # Crear un kiosco de prueba
    kiosk = Kiosk(
        name='Kiosco de Prueba',
        location='Ubicación del Kiosco',
        is_active=True
    )
    
    # Guardar datos en la base de datos
    db.session.add_all([admin, staff, event1, event2, kiosk])
    db.session.commit()
    
    # Crear algunos visitantes de prueba
    visitor1 = Visitor(
        name='Visitante 1',
        email='visitante1@test.com',
        phone='+1234567890',
        event_id=event1.id
    )
    
    visitor2 = Visitor(
        name='Visitante 2',
        email='visitante2@test.com',
        phone='+0987654321',
        event_id=event1.id
    )
    
    visitor3 = Visitor(
        name='Visitante 3',
        email='visitante3@test.com',
        phone='+1122334455',
        event_id=event2.id
    )
    
    db.session.add_all([visitor1, visitor2, visitor3])
    db.session.commit()

@pytest.fixture(scope='session')
def db(app):
    """
    Proporciona acceso a la base de datos de prueba
    """
    with app.app_context():
        yield _db

@pytest.fixture(scope='function')
def session(db):
    """
    Crea una nueva sesión de base de datos para cada prueba
    """
    connection = db.engine.connect()
    transaction = connection.begin()
    
    session = db.create_scoped_session(
        options={"bind": connection, "binds": {}}
    )
    db.session = session
    
    yield session
    
    transaction.rollback()
    connection.close()
    session.remove()

@pytest.fixture
def client(app):
    """
    Proporciona un cliente de pruebas para la aplicación Flask
    """
    with app.test_client() as client:
        yield client

@pytest.fixture
def admin_token(client):
    """
    Proporciona un token de autenticación para un usuario administrador
    """
    response = client.post('/api/v1/auth/login', json={
        'username': 'admin_test',
        'password': 'admin_password'
    })
    
    return response.json['access_token']

@pytest.fixture
def staff_token(client):
    """
    Proporciona un token de autenticación para un usuario de personal
    """
    response = client.post('/api/v1/auth/login', json={
        'username': 'staff_test',
        'password': 'staff_password'
    })
    
    return response.json['access_token']

@pytest.fixture
def auth_headers():
    """
    Proporciona una función para generar encabezados de autenticación
    """
    def _auth_headers(token):
        return {'Authorization': f'Bearer {token}'}
    
    return _auth_headers 