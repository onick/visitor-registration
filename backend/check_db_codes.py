#!/usr/bin/env python3
"""
Script para verificar códigos de registro en la base de datos
"""
import sys
sys.path.append('.')

from app import app, db
from models.visitor import Visitor
from models.event import Event

def check_registration_codes():
    with app.app_context():
        print("=== VERIFICACIÓN DE CÓDIGOS DE REGISTRO ===\n")
        
        # 1. Mostrar todos los visitantes con sus códigos
        visitors = Visitor.query.order_by(Visitor.id.desc()).limit(5).all()
        print("Últimos 5 visitantes:")
        print("-" * 50)
        for visitor in visitors:
            print(f"ID: {visitor.id}")
            print(f"Nombre: {visitor.name}")
            print(f"Email: {visitor.email}")
            print(f"Código: '{visitor.registration_code}'")
            print(f"Longitud del código: {len(visitor.registration_code) if visitor.registration_code else 0}")
            print("-" * 50)
        
        # 2. Crear un nuevo visitante y verificar su código
        print("\nCreando nuevo visitante...")
        new_visitor = Visitor(
            name="Test Direct",
            email="test_direct@example.com",
            phone="809-555-9999"
        )
        db.session.add(new_visitor)
        db.session.commit()
        
        print(f"Nuevo visitante creado:")
        print(f"ID: {new_visitor.id}")
        print(f"Código: '{new_visitor.registration_code}'")
        print(f"Longitud: {len(new_visitor.registration_code) if new_visitor.registration_code else 0}")
        
        # 3. Buscar por código
        print(f"\nBuscando por código '{new_visitor.registration_code}'...")
        found = Visitor.query.filter_by(registration_code=new_visitor.registration_code).first()
        if found:
            print(f"✓ Encontrado: {found.name}")
        else:
            print("✗ No encontrado")
        
        # 4. Buscar por código en mayúsculas
        print(f"\nBuscando por código en mayúsculas '{new_visitor.registration_code.upper()}'...")
        found = Visitor.query.filter_by(registration_code=new_visitor.registration_code.upper()).first()
        if found:
            print(f"✓ Encontrado: {found.name}")
        else:
            print("✗ No encontrado")

if __name__ == "__main__":
    check_registration_codes()
