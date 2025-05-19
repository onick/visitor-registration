from flask import Flask
from models.database import db
from models.user import User
from models.event import Event
from models.visitor import Visitor, VisitorCheckIn
from models.kiosk import Kiosk
from models.notification import Notification
from datetime import datetime
import os

app = Flask(__name__)

# Configurar la base de datos
db_path = os.path.join(os.path.dirname(__file__), 'app.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def init_db():
    with app.app_context():
        # Crear todas las tablas
        db.create_all()
        
        # Verificar si ya existe un usuario admin
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # Crear usuario admin
            admin = User(
                username='admin',
                email='admin@ccb.do',
                first_name='Administrador',
                last_name='Sistema',
                role='admin',
                is_active=True,
                created_at=datetime.utcnow()
            )
            admin.set_password('Admin123!')
            db.session.add(admin)
            db.session.commit()
            print("Usuario admin creado con éxito.")
        else:
            print("El usuario admin ya existe.")
        
        # Verificar si ya existen eventos
        events_count = Event.query.count()
        if events_count == 0:
            # Crear eventos de ejemplo
            events = [
                Event(
                    title="Exposición de Arte Contemporáneo",
                    description="Una fascinante muestra de artistas contemporáneos locales e internacionales, presentando obras que exploran temas sociales actuales a través de diversos medios como pintura, escultura y arte digital.",
                    start_date=datetime.fromisoformat("2025-05-08T07:26:30.967861"),
                    end_date=datetime.fromisoformat("2025-05-08T13:26:30.967861"),
                    location="Sala Principal",
                    image_url="/images/event1.jpg",
                    is_active=True
                ),
                Event(
                    title="Concierto de Música Clásica",
                    description="Disfrute de un repertorio de piezas clásicas interpretadas por la Orquesta Sinfónica Nacional, incluyendo obras de Beethoven, Mozart y compositores dominicanos.",
                    start_date=datetime.fromisoformat("2025-05-08T14:26:30.967861"),
                    end_date=datetime.fromisoformat("2025-05-08T16:26:30.967861"),
                    location="Auditorio",
                    image_url="/images/event2.jpg",
                    is_active=True
                ),
                Event(
                    title="Taller de Literatura",
                    description="Taller interactivo donde reconocidos escritores compartirán técnicas de escritura creativa y análisis literario, con enfoque en la narrativa caribeña contemporánea.",
                    start_date=datetime.fromisoformat("2025-05-09T09:26:30.967861"),
                    end_date=datetime.fromisoformat("2025-05-09T12:26:30.967861"),
                    location="Sala de Conferencias",
                    image_url="/images/event3.jpg",
                    is_active=True
                ),
                Event(
                    title="Exhibición Fotográfica",
                    description="Una colección de fotografías históricas que documenta la evolución urbanística de Santo Domingo durante el último siglo, con imágenes nunca antes expuestas.",
                    start_date=datetime.fromisoformat("2025-05-15T09:26:30.967861"),
                    end_date=datetime.fromisoformat("2025-05-22T09:26:30.967861"),
                    location="Galería Este",
                    image_url="/images/event4.jpg",
                    is_active=True
                ),
                Event(
                    title="Conferencia de Historia",
                    description="Ciclo de conferencias sobre la historia colonial de la República Dominicana, impartidas por historiadores especializados y con documentos históricos originales en exhibición.",
                    start_date=datetime.fromisoformat("2025-05-18T09:26:30.967861"),
                    end_date=datetime.fromisoformat("2025-05-18T11:26:30.967861"),
                    location="Sala de Conferencias",
                    image_url="/images/event5.jpg",
                    is_active=False
                )
            ]
            
            db.session.add_all(events)
            db.session.commit()
            print(f"Se han creado {len(events)} eventos de ejemplo.")
        else:
            print(f"Ya existen {events_count} eventos en la base de datos.")

if __name__ == "__main__":
    init_db()
    print("Base de datos inicializada correctamente.") 