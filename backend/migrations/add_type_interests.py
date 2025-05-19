"""
Script de migración para añadir campos type e interests
"""
import os
import sys
import json
from datetime import datetime
from sqlalchemy import text

# Añadir el directorio actual al path para importar los modelos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import db
from models.event import Event
from models.visitor import Visitor
from app_production import app, create_app

def migrate_database():
    """Aplicar las migraciones a la base de datos"""
    app = create_app()
    
    with app.app_context():
        # Verificar si ya existe la columna type en events
        event_type_exists = False
        visitor_interests_exists = False
        
        try:
            # Verificar columna type en events
            events = db.session.query(Event).first()
            if events:
                if hasattr(events, 'type'):
                    event_type_exists = True
                    print("La columna 'type' ya existe en la tabla events")
        except Exception as e:
            print(f"Error al verificar columna type: {str(e)}")
        
        try:
            # Verificar columna interests en visitors
            visitors = db.session.query(Visitor).first()
            if visitors:
                if hasattr(visitors, 'interests'):
                    visitor_interests_exists = True
                    print("La columna 'interests' ya existe en la tabla visitors")
        except Exception as e:
            print(f"Error al verificar columna interests: {str(e)}")
        
        # Comenzar la migración
        try:
            # Agregar columna type a events si no existe
            if not event_type_exists:
                print("Añadiendo columna 'type' a la tabla events...")
                db.engine.execute(text("ALTER TABLE events ADD COLUMN type VARCHAR(50) DEFAULT 'otro'"))
                print("Columna 'type' añadida correctamente")
            
            # Agregar columna interests a visitors si no existe
            if not visitor_interests_exists:
                print("Añadiendo columna 'interests' a la tabla visitors...")
                db.engine.execute(text("ALTER TABLE visitors ADD COLUMN interests TEXT DEFAULT '[]'"))
                print("Columna 'interests' añadida correctamente")
                
                # Inicializar intereses para cada visitante
                visitors = db.session.query(Visitor).all()
                for visitor in visitors:
                    visitor.interests = '[]'
                db.session.commit()
                print(f"Inicializados intereses para {len(visitors)} visitantes")
            
            # Asignar tipos de eventos (ejemplos)
            events = db.session.query(Event).all()
            event_types = ['cine', 'exposición', 'charla', 'taller', 'concierto', 'exhibición']
            for i, event in enumerate(events):
                # Asignar un tipo según el índice, de forma cíclica
                event.type = event_types[i % len(event_types)]
            db.session.commit()
            print(f"Asignados tipos para {len(events)} eventos")
            
            # Calcular intereses para cada visitante
            visitors = db.session.query(Visitor).all()
            for visitor in visitors:
                visitor.calculate_interests(db.session)
            db.session.commit()
            print(f"Calculados intereses para {len(visitors)} visitantes")
            
            print("Migración completada exitosamente")
        except Exception as e:
            db.session.rollback()
            print(f"Error durante la migración: {str(e)}")

if __name__ == "__main__":
    migrate_database()
