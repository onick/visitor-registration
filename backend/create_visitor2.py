from app import create_app
from models.visitor import Visitor
from models.database import db
import datetime

app = create_app()
ctx = app.app_context()
ctx.push()

def create_test_visitor():
    try:
        # Verificar si el visitante ya existe
        existing_visitor = Visitor.query.filter_by(email="maria@ejemplo.com").first()
        
        if existing_visitor:
            print(f"El visitante con email maria@ejemplo.com ya existe (ID: {existing_visitor.id})")
            return existing_visitor
        
        # Crear nuevo visitante
        new_visitor = Visitor(
            name="María Rodríguez",
            email="maria@ejemplo.com",
            phone="809-555-5678"
        )
        
        # Guardar en la base de datos
        db.session.add(new_visitor)
        db.session.commit()
        
        print(f"Visitante creado con éxito (ID: {new_visitor.id})")
        return new_visitor
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al crear el visitante: {str(e)}")
        return None

if __name__ == "__main__":
    create_test_visitor() 