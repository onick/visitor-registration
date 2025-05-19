from flask import Flask
from models.database import db
from models.event import Event
from datetime import datetime
from sqlalchemy import inspect

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def create_test_event():
    with app.app_context():
        # Verificar si la tabla existe
        inspector = inspect(db.engine)
        if 'events' not in inspector.get_table_names():
            print("La tabla 'events' no existe. Creándola...")
            db.create_all()
        
        # Crear un evento de prueba
        new_event = Event(
            title="Recital de Poesía",
            description="Lectura de poemas de autores dominicanos contemporáneos",
            start_date=datetime.fromisoformat("2023-12-01T18:00:00"),
            end_date=datetime.fromisoformat("2023-12-01T20:00:00"),
            location="Sala de Conferencias",
            is_active=True
        )
        
        try:
            db.session.add(new_event)
            db.session.commit()
            print(f"Evento creado con ID: {new_event.id}")
            return new_event
        except Exception as e:
            db.session.rollback()
            print(f"Error al crear el evento: {e}")
            return None

if __name__ == "__main__":
    created_event = create_test_event()
    if created_event:
        print(f"Evento creado: {created_event.title}")
    else:
        print("No se pudo crear el evento.") 