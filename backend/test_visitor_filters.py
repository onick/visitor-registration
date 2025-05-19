"""
Script de prueba para filtros de visitantes por evento
"""
import sys
import os
from datetime import datetime

# Agregar el directorio raíz al path para importar los modelos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models.visitor import Visitor, VisitorCheckIn
from models.event import Event

def test_visitor_filters():
    """Probar los filtros de visitantes por evento"""
    with app.app_context():
        print("=== PRUEBA DE FILTROS DE VISITANTES POR EVENTO ===")
        print(f"Fecha: {datetime.now()}\n")
        
        # 1. Listar todos los eventos
        print("1. EVENTOS DISPONIBLES:")
        events = Event.query.all()
        for event in events:
            print(f"  - ID: {event.id}, Título: {event.title}")
        
        # 2. Para cada evento, mostrar sus visitantes
        print("\n2. VISITANTES POR EVENTO:")
        for event in events:
            # Obtener visitantes del evento
            visitors_query = db.session.query(
                Visitor,
                VisitorCheckIn
            ).join(
                VisitorCheckIn, 
                Visitor.id == VisitorCheckIn.visitor_id
            ).filter(
                VisitorCheckIn.event_id == event.id
            )
            
            visitors = visitors_query.all()
            
            print(f"\nEvento: {event.title} (ID: {event.id})")
            print(f"Total de visitantes: {len(visitors)}")
            
            if visitors:
                for visitor, checkin in visitors:
                    print(f"  - {visitor.name} ({visitor.email})")
                    print(f"    Código: {visitor.registration_code}")
                    print(f"    Check-in: {checkin.check_in_time}")
            else:
                print("  No hay visitantes registrados")
        
        # 3. Probar búsqueda de visitantes con filtro
        print("\n3. BÚSQUEDA DE VISITANTES CON FILTROS:")
        
        # Buscar por email
        email_search = "maria@example.com"
        visitor_by_email = Visitor.query.filter_by(email=email_search).first()
        if visitor_by_email:
            print(f"\nVisitante con email '{email_search}':")
            print(f"  - Nombre: {visitor_by_email.name}")
            print(f"  - Código: {visitor_by_email.registration_code}")
            
            # Buscar eventos donde está registrado
            events_registered = db.session.query(Event).join(
                VisitorCheckIn,
                Event.id == VisitorCheckIn.event_id
            ).filter(
                VisitorCheckIn.visitor_id == visitor_by_email.id
            ).all()
            
            print(f"  - Registrado en {len(events_registered)} eventos:")
            for event in events_registered:
                print(f"    * {event.title}")
        
        # 4. Verificar filtro por event_id
        print("\n4. FILTRO POR EVENT_ID:")
        if events:
            test_event_id = events[0].id
            print(f"\nFiltrando visitantes del evento ID {test_event_id}:")
            
            # Simulando el query del endpoint
            query = Visitor.query
            query = query.join(VisitorCheckIn).filter(VisitorCheckIn.event_id == test_event_id)
            filtered_visitors = query.all()
            
            print(f"Visitantes encontrados: {len(filtered_visitors)}")
            for visitor in filtered_visitors:
                print(f"  - {visitor.name} ({visitor.email})")
        
        # 5. Verificar join sin visitantes
        print("\n5. EVENTOS SIN VISITANTES:")
        empty_events = []
        for event in events:
            count = VisitorCheckIn.query.filter_by(event_id=event.id).count()
            if count == 0:
                empty_events.append(event)
        
        if empty_events:
            print(f"Eventos sin visitantes: {len(empty_events)}")
            for event in empty_events:
                print(f"  - {event.title}")
        else:
            print("Todos los eventos tienen al menos un visitante")
        
        print("\n=== FIN DE LA PRUEBA ===")

if __name__ == "__main__":
    test_visitor_filters()
