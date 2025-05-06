"""
Script para inicializar la base de datos con datos de prueba
"""
from models.database import db
from models.event import Event
from models.kiosk import Kiosk, KioskConfig
import datetime

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
