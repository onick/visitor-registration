"""
Script para actualizar el modelo de visitantes con el estado CANCELED
"""
from models.database import db
from models.visitor import Visitor, EventVisitor
from models import User
from app import app
import sys

def add_canceled_state():
    """
    Actualiza el modelo de EventVisitor para soportar el estado CANCELED
    """
    with app.app_context():
        # Verificar si ya existe el estado CANCELED en alguna fila
        canceled_exists = db.session.query(EventVisitor).filter(
            EventVisitor.status == 'CANCELED'
        ).first()
        
        if canceled_exists:
            print("El estado CANCELED ya existe en al menos una fila.")
            return
        
        try:
            # Mostrar información sobre los registros existentes
            registrations = EventVisitor.query.count()
            print(f"Total de registros actuales: {registrations}")
            
            # Estadísticas de estados actuales
            for status in ['REGISTERED', 'CHECKED_IN', 'NO_SHOW']:
                count = EventVisitor.query.filter(EventVisitor.status == status).count()
                print(f"  - {status}: {count}")
            
            # Crear algunos registros de prueba con estado CANCELED
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                print("Error: No se encontró al usuario administrador.")
                return
                
            # Obtener algunos visitantes y eventos para las pruebas
            visitors = Visitor.query.limit(2).all()
            
            if not visitors:
                print("Error: No se encontraron visitantes para las pruebas.")
                return
                
            # Crear registros de prueba
            for visitor in visitors:
                # Buscar un registro existente para este visitante
                existing = EventVisitor.query.filter_by(visitor_id=visitor.id).first()
                
                if existing:
                    print(f"Creando registro de prueba CANCELED para el visitante {visitor.name} en el evento {existing.event_id}")
                    
                    # Crear un nuevo registro para este visitante con estado CANCELED
                    canceled_reg = EventVisitor(
                        visitor_id=visitor.id,
                        event_id=existing.event_id,
                        registration_code=visitor.registration_code,
                        registered_by=admin_user.id,
                        status='CANCELED',
                        registration_date=db.func.now(),
                        notes="Registro cancelado como parte de la actualización del modelo"
                    )
                    
                    db.session.add(canceled_reg)
            
            # Commit de los cambios
            db.session.commit()
            print("Se han creado registros de prueba con estado CANCELED.")
            
            # Estadísticas después de los cambios
            for status in ['REGISTERED', 'CHECKED_IN', 'NO_SHOW', 'CANCELED']:
                count = EventVisitor.query.filter(EventVisitor.status == status).count()
                print(f"  - {status}: {count}")
                
            print("Actualización completada exitosamente.")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error al actualizar el modelo: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    add_canceled_state() 