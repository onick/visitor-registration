"""
Script para verificar el problema con los visitantes y eventos
"""
import sys
import os
from datetime import datetime

# Agregar el directorio raíz al path para importar los modelos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models.visitor import Visitor, VisitorCheckIn
from models.event import Event

def debug_visitor_event_relationship():
    """Depurar la relación entre visitantes y eventos"""
    with app.app_context():
        print("=== DEPURACIÓN DE VISITANTES Y EVENTOS ===")
        print(f"Fecha: {datetime.now()}\n")
        
        # 1. Verificar la estructura de las tablas
        print("1. VERIFICANDO ESTRUCTURA DE TABLAS")
        
        # Listar todas las tablas
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Tablas en la base de datos: {tables}")
        
        # Verificar columnas de visitor_check_ins
        if 'visitor_check_ins' in tables:
            columns = inspector.get_columns('visitor_check_ins')
            print("\nColumnas en visitor_check_ins:")
            for col in columns:
                print(f"  - {col['name']} ({col['type']})")
        
        # 2. Verificar relaciones en el ORM
        print("\n2. VERIFICANDO RELACIONES ORM")
        print(f"Modelo Visitor tiene relación 'check_ins': {'check_ins' in dir(Visitor)}")
        print(f"Modelo VisitorCheckIn tiene relación 'visitor': {'visitor' in dir(VisitorCheckIn)}")
        print(f"Modelo VisitorCheckIn tiene relación 'event': {'event' in dir(VisitorCheckIn)}")
        
        # 3. Consultar visitantes con sus eventos
        print("\n3. CONSULTANDO VISITANTES CON EVENTOS")
        
        # Método 1: Usando join directo
        visitors_with_events = db.session.query(
            Visitor, 
            VisitorCheckIn, 
            Event
        ).join(
            VisitorCheckIn, 
            Visitor.id == VisitorCheckIn.visitor_id
        ).join(
            Event,
            VisitorCheckIn.event_id == Event.id
        ).all()
        
        print(f"\nVisitantes con eventos (join directo): {len(visitors_with_events)}")
        for visitor, checkin, event in visitors_with_events[:5]:  # Mostrar solo los primeros 5
            print(f"\nVisitante: {visitor.name}")
            print(f"  Email: {visitor.email}")
            print(f"  Código: {visitor.registration_code}")
            print(f"  Evento: {event.title}")
            print(f"  Check-in: {checkin.check_in_time}")
        
        # 4. Verificar visitantes sin eventos
        print("\n4. VERIFICANDO VISITANTES SIN EVENTOS")
        
        # Visitantes que no tienen registros en visitor_check_ins
        visitors_without_events = db.session.query(Visitor).filter(
            ~Visitor.id.in_(
                db.session.query(VisitorCheckIn.visitor_id).distinct()
            )
        ).all()
        
        print(f"Visitantes sin eventos: {len(visitors_without_events)}")
        for visitor in visitors_without_events[:5]:
            print(f"  - {visitor.name} ({visitor.email})")
        
        # 5. Verificar la consulta que usa el endpoint
        print("\n5. SIMULANDO CONSULTA DEL ENDPOINT")
        
        # Esta es la misma consulta que usa el endpoint actualizado
        query = db.session.query(
            Visitor,
            VisitorCheckIn,
            Event
        ).join(
            VisitorCheckIn, 
            Visitor.id == VisitorCheckIn.visitor_id,
            isouter=True
        ).join(
            Event,
            VisitorCheckIn.event_id == Event.id,
            isouter=True
        )
        
        results = query.all()
        print(f"\nResultados de la consulta con outer join: {len(results)}")
        
        # Analizar los resultados
        for visitor, checkin, event in results[:5]:
            print(f"\nVisitante: {visitor.name}")
            print(f"  Email: {visitor.email}")
            print(f"  Código: {visitor.registration_code}")
            
            if event:
                print(f"  Evento: {event.title}")
                print(f"  Fecha: {event.start_date}")
            else:
                print("  Evento: SIN EVENTO (checkin es None o evento eliminado)")
            
            if checkin:
                print(f"  Check-in ID: {checkin.id}")
                print(f"  Event ID en check-in: {checkin.event_id}")
            else:
                print("  Check-in: NO HAY REGISTRO DE CHECK-IN")
        
        # 6. Crear datos de prueba
        print("\n6. CREANDO DATOS DE PRUEBA")
        
        # Crear un evento de prueba
        test_event = Event(
            title="Evento Test Debug",
            description="Evento para depuración",
            start_date=datetime.now(),
            end_date=datetime.now().replace(hour=20),
            location="Sala Debug",
            is_active=True
        )
        db.session.add(test_event)
        db.session.flush()
        
        # Crear un visitante de prueba
        test_visitor = Visitor(
            name="Debug Visitor",
            email=f"debug.visitor.{int(datetime.now().timestamp())}@example.com",
            phone="809-555-DEBUG"
        )
        db.session.add(test_visitor)
        db.session.flush()
        
        # Registrar el visitante para el evento
        test_checkin = VisitorCheckIn(
            visitor_id=test_visitor.id,
            event_id=test_event.id,
            kiosk_id=1
        )
        db.session.add(test_checkin)
        db.session.commit()
        
        print(f"Creado evento: {test_event.title} (ID: {test_event.id})")
        print(f"Creado visitante: {test_visitor.name} (ID: {test_visitor.id})")
        print(f"Creado check-in: ID {test_checkin.id}")
        
        # 7. Verificar que aparece correctamente
        print("\n7. VERIFICANDO DATOS DE PRUEBA")
        
        # Buscar el visitante con su evento
        result = db.session.query(
            Visitor,
            VisitorCheckIn,
            Event
        ).filter(
            Visitor.id == test_visitor.id
        ).join(
            VisitorCheckIn, 
            Visitor.id == VisitorCheckIn.visitor_id
        ).join(
            Event,
            VisitorCheckIn.event_id == Event.id
        ).first()
        
        if result:
            visitor, checkin, event = result
            print(f"\nVisitante encontrado: {visitor.name}")
            print(f"  Evento asociado: {event.title}")
            print(f"  Registro confirmado correctamente")
        else:
            print("\nERROR: No se encontró el visitante de prueba con su evento")
        
        print("\n=== FIN DE LA DEPURACIÓN ===")

if __name__ == "__main__":
    debug_visitor_event_relationship()
