"""
Script para inicializar la base de datos con datos de prueba
"""
import os
import sys

# Añadir el directorio raíz al path para poder importar módulos
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from models.database import db
from models.event import Event
from models.kiosk import Kiosk, KioskConfig
from models.user import User
from models.visitor import Visitor, VisitorCheckIn
from models.notification import Notification
import datetime

def init_database():
    """
    Inicializar la base de datos creando todas las tablas
    """
    db.create_all()
    print("Base de datos inicializada - tablas creadas")

def create_admin_user(email="admin@ccb.do", password="Admin123!", first_name="Administrador", last_name="Sistema"):
    """
    Crear un usuario administrador si no existe
    """
    # Verificar si ya existe un administrador
    admin = User.query.filter_by(role='admin').first()
    if admin:
        print(f"Usuario administrador ya existe: {admin.email}")
        return admin.id
    
    # Crear un nuevo administrador
    admin = User(
        username="admin",
        email=email,
        first_name=first_name,
        last_name=last_name,
        role="admin",
        is_active=True,
        created_at=datetime.datetime.utcnow()
    )
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()
    
    print(f"Usuario administrador creado: {admin.email}")
    return admin.id

def create_sample_data():
    """
    Crear datos de ejemplo para pruebas
    """
    # Limpiar tablas
    db.session.query(Event).delete()
    db.session.query(KioskConfig).delete()
    db.session.query(Kiosk).delete()
    db.session.commit()
    
    # Crear kiosco de prueba
    kiosk = Kiosk(
        name="Kiosco Entrada Principal",
        location="Lobby",
        is_active=True
    )
    db.session.add(kiosk)
    db.session.flush()  # Para obtener el ID
    
    # Configuración del kiosco
    kiosk_config = KioskConfig(
        kiosk_id=kiosk.id,
        language="es",
        idle_timeout=60,
        custom_message="¡Bienvenido al Centro Cultural Banreservas!"
    )
    db.session.add(kiosk_config)
    
    # Crear eventos de prueba
    now = datetime.datetime.now()
    
    # Evento actual (en curso)
    event1 = Event(
        title="Exposición de Arte Contemporáneo",
        description="Una fascinante muestra de artistas contemporáneos locales e internacionales, presentando obras que exploran temas sociales actuales a través de diversos medios como pintura, escultura y arte digital.",
        start_date=now - datetime.timedelta(hours=2),
        end_date=now + datetime.timedelta(hours=4),
        location="Sala Principal",
        image_url="/images/event1.jpg",
        is_active=True
    )
    
    # Evento próximo (hoy, más tarde)
    event2 = Event(
        title="Concierto de Música Clásica",
        description="Disfrute de un repertorio de piezas clásicas interpretadas por la Orquesta Sinfónica Nacional, incluyendo obras de Beethoven, Mozart y compositores dominicanos.",
        start_date=now + datetime.timedelta(hours=5),
        end_date=now + datetime.timedelta(hours=7),
        location="Auditorio",
        image_url="/images/event2.jpg",
        is_active=True
    )
    
    # Evento para mañana
    event3 = Event(
        title="Taller de Literatura",
        description="Taller interactivo donde reconocidos escritores compartirán técnicas de escritura creativa y análisis literario, con enfoque en la narrativa caribeña contemporánea.",
        start_date=now + datetime.timedelta(days=1),
        end_date=now + datetime.timedelta(days=1, hours=3),
        location="Sala de Conferencias",
        image_url="/images/event3.jpg",
        is_active=True
    )
    
    # Evento para la próxima semana
    event4 = Event(
        title="Exhibición Fotográfica",
        description="Una colección de fotografías históricas que documenta la evolución urbanística de Santo Domingo durante el último siglo, con imágenes nunca antes expuestas.",
        start_date=now + datetime.timedelta(days=7),
        end_date=now + datetime.timedelta(days=14),
        location="Galería Este",
        image_url="/images/event4.jpg",
        is_active=True
    )
    
    # Evento inactivo (para pruebas)
    event5 = Event(
        title="Conferencia de Historia",
        description="Ciclo de conferencias sobre la historia colonial de la República Dominicana, impartidas por historiadores especializados y con documentos históricos originales en exhibición.",
        start_date=now + datetime.timedelta(days=10),
        end_date=now + datetime.timedelta(days=10, hours=2),
        location="Sala de Conferencias",
        image_url="/images/event5.jpg",
        is_active=False
    )
    
    db.session.add_all([event1, event2, event3, event4, event5])
    db.session.commit()
    
    print("Datos de muestra creados exitosamente")
    return {
        "kiosk_id": kiosk.id,
        "events": [event1.id, event2.id, event3.id, event4.id, event5.id]
    }

if __name__ == "__main__":
    # Importar la aplicación para tener el contexto de base de datos
    from app import create_app
    
    # Configurar variables de entorno para desarrollo
    os.environ['FLASK_ENV'] = 'development'
    os.environ['USE_SQLITE'] = 'true'
    os.environ['ADMIN_EMAIL'] = 'admin@ccb.do'
    os.environ['ADMIN_PASSWORD'] = 'Admin123!'
    
    app = create_app({
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///dev.db'
    })
    
    with app.app_context():
        # Inicializar la base de datos
        init_database()
        
        # Crear usuario administrador
        admin_id = create_admin_user()
        
        # Crear datos de ejemplo si se desea
        create_sample_data()
        
        print("Inicialización de base de datos completada")
