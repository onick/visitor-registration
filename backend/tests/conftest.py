"""
Configuraciones y fixtures para las pruebas de la API de registro de visitantes
"""
import os
import pytest
import tempfile
from datetime import datetime, timedelta

# Asegurarse de que app y otros módulos se importen desde la raíz del backend
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_root = os.path.dirname(current_dir) # /tests -> /backend
sys.path.insert(0, backend_root)

from app import create_app # Ahora debería funcionar
from models.database import db as _db # Renombrar para evitar conflicto con fixture
from models.user import User
from models.event import Event
from models.visitor import Visitor # Asumiendo que existe este modelo
from models.kiosk import Kiosk     # Asumiendo que existe este modelo

USER_PASSWORD = "TestPassword123!"
ADMIN_PASSWORD = "AdminPassword123!"
STAFF_PASSWORD = "StaffPassword123!"

@pytest.fixture(scope='session')
def app():
    """
    Crea una instancia de la aplicación Flask para las pruebas.
    """
    db_fd, db_path = tempfile.mkstemp()

    config_override = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}', # O 'sqlite:///:memory:'
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'JWT_SECRET_KEY': 'test-secret-key',
        'MAX_LOGIN_ATTEMPTS': 3, # Para probar bloqueo más rápido
        'ACCOUNT_LOCKOUT_MINUTES': 1, # Para probar desbloqueo más rápido (si se implementa)
        'WTF_CSRF_ENABLED': False, # Deshabilitar CSRF para pruebas si se usa Flask-WTF
        'DEBUG': False # Asegurarse que DEBUG esté apagado para que FLASK_ENV no lo sobreescriba
    }

    _app = create_app(config_override)

    with _app.app_context():
        _db.create_all()
        yield _app # Devuelve la app aquí para que el contexto esté activo
    
    # Limpieza después de que todas las pruebas de la sesión terminen
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture(scope='session')
def db(app):
    """Fixture de base de datos para toda la sesión."""
    # _db.app = app # No es necesario si se inicializa con app.app_context()
    # with app.app_context(): # El contexto ya está activo desde la fixture app
    #     _db.create_all() # Ya se hizo en la fixture app
    yield _db
    # with app.app_context(): # El contexto ya está activo
    #     _db.drop_all() # Limpiar después de las pruebas si no se usa BBDD en memoria

@pytest.fixture(scope='function')
def session(app, db):
    """Rolls back database changes after each test."""
    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()

        # Aquí podrías limpiar todas las tablas si prefieres un estado completamente virgen
        # en lugar de depender solo del rollback.
        # for table in reversed(db.metadata.sorted_tables):
        #     db.session.execute(table.delete())
        # db.session.commit()

        # Crear datos base para cada test si es necesario, o usar fixtures específicas
        _create_base_users(db)

        yield db.session

        db.session.remove()
        transaction.rollback()
        connection.close()

def _create_base_users(db_instance):
    """Crea usuarios base si no existen, usado por la sesión de prueba."""
    if not User.query.filter_by(username='admin_test').first():
        admin = User(username='admin_test', email='admin@test.com', first_name='Admin', last_name='User', role='admin', is_active=True)
        admin.set_password(ADMIN_PASSWORD)
        db_instance.session.add(admin)

    if not User.query.filter_by(username='staff_test').first():
        staff = User(username='staff_test', email='staff@test.com', first_name='Staff', last_name='User', role='staff', is_active=True)
        staff.set_password(STAFF_PASSWORD)
        db_instance.session.add(staff)
    
    db_instance.session.commit()

@pytest.fixture(scope='function')
def registered_user(session):
    """Crea y devuelve un usuario registrado estándar y activo con login_attempts reseteado."""
    user = User.query.filter_by(username='testuser').first()
    if not user:
        user = User(username='testuser', email='test@example.com', first_name='Test', last_name='User', role='staff', is_active=True)
        user.set_password(USER_PASSWORD)
        session.add(user)
    # Asegurar que los intentos estén reseteados para esta instancia de prueba
    user.login_attempts = 0
    user.locked_until = None
    session.commit()
    return user, USER_PASSWORD

@pytest.fixture(scope='function')
def inactive_user(session):
    """Crea y devuelve un usuario registrado pero inactivo con login_attempts reseteado."""
    user = User.query.filter_by(username='inactiveuser').first()
    if not user:
        user = User(username='inactiveuser', email='inactive@example.com', first_name='Inactive', last_name='User', role='staff', is_active=False)
        user.set_password(USER_PASSWORD)
        session.add(user)
    # Asegurar que los intentos estén reseteados
    user.login_attempts = 0
    user.locked_until = None
    session.commit()
    return user, USER_PASSWORD

@pytest.fixture(scope='function')
def admin_user(session):
    """Devuelve el usuario admin de prueba y su contraseña."""
    user = User.query.filter_by(username='admin_test').first()
    # _create_base_users ya debería haberlo creado en el setup de la session fixture
    return user, ADMIN_PASSWORD

@pytest.fixture(scope='function')
def staff_user(session):
    """Devuelve el usuario staff de prueba y su contraseña."""
    user = User.query.filter_by(username='staff_test').first()
    return user, STAFF_PASSWORD

@pytest.fixture
def client(app, session): # session fixture asegura BBDD limpia y usuarios base
    """Un cliente de prueba de Flask para la aplicación."""
    return app.test_client()

@pytest.fixture
def runner(app, session):
    """Un corredor de cli de Flask."""
    return app.test_cli_runner()

@pytest.fixture
def auth_headers(client):
    """Devuelve una función para crear cabeceras de autorización."""
    def _auth_headers(token):
        return {'Authorization': f'Bearer {token}'}
    return _auth_headers

@pytest.fixture
def get_admin_token(client, admin_user):
    """Obtiene un token de acceso para el usuario admin."""
    user, password = admin_user
    response = client.post('/api/v1/auth/login', json={
        'username': user.username,
        'password': password
    })
    assert response.status_code == 200, f"Login fallido para admin: {response.json}"
    return response.json['access_token']

@pytest.fixture
def get_staff_token(client, staff_user):
    """Obtiene un token de acceso para el usuario staff."""
    user, password = staff_user
    response = client.post('/api/v1/auth/login', json={
        'username': user.username,
        'password': password
    })
    assert response.status_code == 200, f"Login fallido para staff: {response.json}"
    return response.json['access_token']

# Fixture para datos de ejemplo de evento (puedes moverla a un test_events conftest si prefieres)
@pytest.fixture
def sample_event_data():
    return {
        'title': 'Evento de Conferencia Tech',
        'description': 'Una gran conferencia sobre tecnología.',
        'start_date': (datetime.utcnow() + timedelta(days=10)).isoformat() + 'Z',
        'end_date': (datetime.utcnow() + timedelta(days=11)).isoformat() + 'Z',
        'location': 'Centro de Convenciones Principal'
    }

# Fixture para crear un evento en la BBDD (puedes moverla)
@pytest.fixture
def create_event_in_db(session, sample_event_data):
    event = Event(**{
        k: v for k, v in sample_event_data.items() 
        if k not in ['start_date', 'end_date'] # Convertir fechas
    })
    event.start_date = datetime.fromisoformat(sample_event_data['start_date'].replace('Z', '+00:00'))
    event.end_date = datetime.fromisoformat(sample_event_data['end_date'].replace('Z', '+00:00'))
    session.add(event)
    session.commit()
    return event.id

# Comentando tus fixtures originales para evitar conflictos por ahora, 
# las integraremos o reemplazaremos con las de arriba.

# @pytest.fixture(scope='session')
# def app():
#     """
#     Crea una instancia de la aplicación Flask para las pruebas
#     """
#     # Configuración para testing
#     db_fd, db_path = tempfile.mkstemp()
    
#     config = {
#         'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
#         'SQLALCHEMY_TRACK_MODIFICATIONS': False,
#         'TESTING': True,
#         'JWT_SECRET_KEY': 'secret-key-for-testing',
#         'JWT_ACCESS_TOKEN_EXPIRES': timedelta(hours=1),
#         'JWT_REFRESH_TOKEN_EXPIRES': timedelta(days=30),
#     }
    
#     app = create_app(config)
    
#     with app.app_context():
#         _db.create_all()
#         # Crear datos iniciales
#         _setup_test_data(_db)
        
#         yield app
    
#     os.close(db_fd)
#     os.unlink(db_path)

# def _setup_test_data(db):
#     """
#     Configura datos iniciales para las pruebas
#     """
#     # Crear usuarios de prueba (admin y staff)
#     admin = User(
#         username='admin_test',
#         email='admin@test.com',
#         first_name='Admin',
#         last_name='Test',
#         role='admin',
#         is_active=True
#     )
#     admin.set_password('admin_password')
    
#     staff = User(
#         username='staff_test',
#         email='staff@test.com',
#         first_name='Staff',
#         last_name='Test',
#         role='staff',
#         is_active=True
#     )
#     staff.set_password('staff_password')
    
#     # Crear algunos eventos de prueba
#     event1 = Event(
#         title='Evento de Prueba 1',
#         description='Descripción del evento de prueba 1',
#         start_date=datetime.utcnow() + timedelta(days=1),
#         end_date=datetime.utcnow() + timedelta(days=2),
#         location='Ubicación 1',
#         is_active=True
#     )
    
#     event2 = Event(
#         title='Evento de Prueba 2',
#         description='Descripción del evento de prueba 2',
#         start_date=datetime.utcnow() + timedelta(days=3),
#         end_date=datetime.utcnow() + timedelta(days=4),
#         location='Ubicación 2',
#         is_active=True
#     )
    
#     # Crear un kiosco de prueba
#     kiosk = Kiosk(
#         name='Kiosco de Prueba',
#         location='Ubicación del Kiosco',
#         is_active=True
#     )
    
#     # Guardar datos en la base de datos
#     db.session.add_all([admin, staff, event1, event2, kiosk])
#     db.session.commit()
    
#     # Crear algunos visitantes de prueba
#     visitor1 = Visitor(
#         name='Visitante 1',
#         email='visitante1@test.com',
#         phone='+1234567890',
#         event_id=event1.id
#     )
    
#     visitor2 = Visitor(
#         name='Visitante 2',
#         email='visitante2@test.com',
#         phone='+0987654321',
#         event_id=event1.id
#     )
    
#     visitor3 = Visitor(
#         name='Visitante 3',
#         email='visitante3@test.com',
#         phone='+1122334455',
#         event_id=event2.id
#     )
    
#     db.session.add_all([visitor1, visitor2, visitor3])
#     db.session.commit()

# @pytest.fixture(scope='session')
# def db(app):
#     """
#     Proporciona acceso a la base de datos de prueba
#     """
#     with app.app_context():
#         yield _db

# @pytest.fixture(scope='function')
# def session(db):
#     """
#     Crea una nueva sesión de base de datos para cada prueba
#     """
#     connection = db.engine.connect()
#     transaction = connection.begin()
    
#     session = db.create_scoped_session(
#         options={"bind": connection, "binds": {}}
#     )
#     db.session = session
    
#     yield session
    
#     transaction.rollback()
#     connection.close()
#     session.remove()

# @pytest.fixture
# def client(app):
#     """
#     Proporciona un cliente de pruebas para la aplicación Flask
#     """
#     with app.test_client() as client:
#         yield client

# @pytest.fixture
# def admin_token(client):
#     """
#     Proporciona un token de autenticación para un usuario administrador
#     """
#     response = client.post('/api/v1/auth/login', json={
#         'username': 'admin_test',
#         'password': 'admin_password'
#     })
    
#     return response.json['access_token']

# @pytest.fixture
# def staff_token(client):
#     """
#     Proporciona un token de autenticación para un usuario de personal
#     """
#     response = client.post('/api/v1/auth/login', json={
#         'username': 'staff_test',
#         'password': 'staff_password'
#     })
    
#     return response.json['access_token']

# @pytest.fixture
# def auth_headers():
#     """
#     Proporciona una función para generar encabezados de autenticación
#     """
#     def _auth_headers(token):
#         return {'Authorization': f'Bearer {token}'}
    
#     return _auth_headers 