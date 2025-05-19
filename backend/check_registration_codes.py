"""
Script para verificar los códigos de registro de visitantes en la base de datos
"""
import sys
import os
from datetime import datetime

# Agregar el directorio raíz al path para importar los modelos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models.visitor import Visitor, VisitorCheckIn
from models.event import Event

def check_registration_codes():
    """Verificar la integridad de los códigos de registro"""
    with app.app_context():
        print("=== VERIFICACIÓN DE CÓDIGOS DE REGISTRO ===")
        print(f"Fecha: {datetime.now()}\n")
        
        # 1. Contar visitantes totales
        total_visitors = Visitor.query.count()
        print(f"Total de visitantes en la base de datos: {total_visitors}")
        
        # 2. Verificar visitantes sin código
        visitors_without_code = Visitor.query.filter(
            db.or_(
                Visitor.registration_code == None,
                Visitor.registration_code == ''
            )
        ).all()
        
        if visitors_without_code:
            print(f"\n⚠️  ADVERTENCIA: {len(visitors_without_code)} visitantes sin código de registro:")
            for visitor in visitors_without_code:
                print(f"  - ID: {visitor.id}, Nombre: {visitor.name}, Email: {visitor.email}")
        else:
            print("\n✅ Todos los visitantes tienen código de registro")
        
        # 3. Verificar duplicados
        codes = {}
        duplicates = []
        all_visitors = Visitor.query.all()
        
        for visitor in all_visitors:
            if visitor.registration_code:
                if visitor.registration_code in codes:
                    duplicates.append((visitor, codes[visitor.registration_code]))
                else:
                    codes[visitor.registration_code] = visitor
        
        if duplicates:
            print(f"\n⚠️  ADVERTENCIA: Se encontraron códigos duplicados:")
            for visitor1, visitor2 in duplicates:
                print(f"  - Código '{visitor1.registration_code}' usado por:")
                print(f"    * ID: {visitor1.id}, Nombre: {visitor1.name}")
                print(f"    * ID: {visitor2.id}, Nombre: {visitor2.name}")
        else:
            print("\n✅ No hay códigos duplicados")
        
        # 4. Verificar formato de códigos
        invalid_format = []
        for visitor in all_visitors:
            if visitor.registration_code:
                if len(visitor.registration_code) != 6 or not visitor.registration_code.isalnum():
                    invalid_format.append(visitor)
        
        if invalid_format:
            print(f"\n⚠️  ADVERTENCIA: {len(invalid_format)} códigos con formato inválido:")
            for visitor in invalid_format:
                print(f"  - ID: {visitor.id}, Código: '{visitor.registration_code}' (longitud: {len(visitor.registration_code)})")
        else:
            print("\n✅ Todos los códigos tienen formato válido (6 caracteres alfanuméricos)")
        
        # 5. Mostrar algunos ejemplos de códigos
        print("\n📋 Ejemplos de códigos registrados:")
        sample_visitors = Visitor.query.limit(10).all()
        for visitor in sample_visitors:
            print(f"  - {visitor.name}: '{visitor.registration_code}'")
        
        # 6. Verificar registros por evento
        print("\n📊 Registros por evento:")
        events = Event.query.all()
        for event in events:
            registrations = VisitorCheckIn.query.filter_by(event_id=event.id).count()
            print(f"  - {event.title}: {registrations} visitantes registrados")
        
        # 7. Buscar un código específico (ejemplo)
        test_code = "ABC123"
        print(f"\n🔍 Prueba de búsqueda - Código '{test_code}':")
        test_visitor = Visitor.query.filter_by(registration_code=test_code).first()
        if test_visitor:
            print(f"  Encontrado: {test_visitor.name}, Email: {test_visitor.email}")
        else:
            print(f"  No se encontró ningún visitante con el código '{test_code}'")
        
        print("\n=== FIN DE LA VERIFICACIÓN ===")

if __name__ == "__main__":
    check_registration_codes()
