#!/usr/bin/env python3
"""
Script para verificar el modelo Visitor y el campo registration_code
"""
import sys
sys.path.append('.')

from app import app, db
from models.visitor import Visitor
from sqlalchemy import inspect

def inspect_visitor_model():
    with app.app_context():
        print("=== INSPECCIÓN DEL MODELO VISITOR ===\n")
        
        # 1. Verificar la estructura de la tabla
        inspector = inspect(db.engine)
        columns = inspector.get_columns('visitors')
        
        print("Columnas de la tabla 'visitors':")
        for col in columns:
            print(f"- {col['name']}: {col['type']} (nullable: {col['nullable']})")
        
        # 2. Crear un visitante de prueba
        print("\n\nCreando visitante de prueba...")
        test_visitor = Visitor(
            name="Inspector Test",
            email="inspector@test.com",
            phone="809-555-7777"
        )
        
        print(f"Antes de guardar:")
        print(f"- registration_code: '{test_visitor.registration_code}'")
        
        db.session.add(test_visitor)
        db.session.commit()
        
        print(f"\nDespués de guardar:")
        print(f"- ID: {test_visitor.id}")
        print(f"- registration_code: '{test_visitor.registration_code}'")
        print(f"- Tipo: {type(test_visitor.registration_code)}")
        print(f"- Longitud: {len(test_visitor.registration_code) if test_visitor.registration_code else 0}")
        
        # 3. Buscar el visitante
        print("\n\nBuscando el visitante...")
        found = Visitor.query.get(test_visitor.id)
        print(f"Encontrado:")
        print(f"- registration_code: '{found.registration_code}'")
        
        # 4. Buscar por código
        print(f"\n\nBuscando por código '{test_visitor.registration_code}'...")
        by_code = Visitor.query.filter_by(registration_code=test_visitor.registration_code).first()
        if by_code:
            print(f"✓ Encontrado: {by_code.name}")
        else:
            print("✗ No encontrado")
            
            # Intentar buscar con LIKE
            print("\nIntentando con LIKE...")
            like_results = Visitor.query.filter(
                Visitor.registration_code.like(f"%{test_visitor.registration_code}%")
            ).all()
            print(f"Resultados: {len(like_results)}")
            for v in like_results:
                print(f"- {v.name}: '{v.registration_code}'")

if __name__ == "__main__":
    inspect_visitor_model()
