from app import create_app
from models.visitor import Visitor, VisitorCheckIn
from models.event import Event
from models.kiosk import Kiosk
from models.database import db
import datetime

app = create_app()
ctx = app.app_context()
ctx.push()

def register_visitor_to_event():
    try:
        # Obtener el visitante
        visitor = Visitor.query.filter_by(email="maria@ejemplo.com").first()
        if not visitor:
            print("El visitante no existe.")
            return None
        
        # Obtener el evento (el segundo evento activo)
        events = Event.query.filter_by(is_active=True).all()
        if len(events) < 2:
            print("No hay suficientes eventos activos disponibles.")
            return None
        
        event = events[1]  # Tomamos el segundo evento activo
        
        # Obtener un kiosco
        kiosk = Kiosk.query.filter_by(is_active=True).first()
        if not kiosk:
            print("No hay kioscos activos disponibles.")
            return None
        
        # Verificar si ya existe un registro para este visitante y evento
        existing_check_in = VisitorCheckIn.query.filter_by(
            visitor_id=visitor.id,
            event_id=event.id
        ).first()
        
        if existing_check_in:
            print(f"El visitante ya está registrado en el evento '{event.title}' (ID: {existing_check_in.id})")
            return existing_check_in
        
        # Crear nuevo registro
        check_in = VisitorCheckIn(
            visitor_id=visitor.id,
            event_id=event.id,
            kiosk_id=kiosk.id,
            check_in_time=datetime.datetime.now()
        )
        
        # Guardar en la base de datos
        db.session.add(check_in)
        db.session.commit()
        
        print(f"Registro creado con éxito (ID: {check_in.id})")
        print(f"Visitante: {visitor.name} (ID: {visitor.id})")
        print(f"Evento: {event.title} (ID: {event.id})")
        print(f"Kiosco: {kiosk.name} (ID: {kiosk.id})")
        print(f"Fecha y hora: {check_in.check_in_time}")
        
        return check_in
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al crear el registro: {str(e)}")
        return None

if __name__ == "__main__":
    register_visitor_to_event() 