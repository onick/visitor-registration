#!/usr/bin/env python3
"""
Script para migrar datos de SQLite a PostgreSQL
"""
import sqlite3
import os
import sys
from datetime import datetime
from sqlalchemy import text

# Agregar el directorio backend al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurar variables de entorno antes de importar la app
os.environ['FLASK_ENV'] = 'production'

from app_production import app, db
from models.visitor import Visitor, VisitorCheckIn
from models.event import Event
from models.user import User
from models.kiosk import Kiosk

def reset_sequences():
    """Reiniciar secuencias de PostgreSQL después de la migración"""
    with app.app_context():
        # Obtener todas las tablas
        tables = ['visitors', 'events', 'users', 'kiosks', 'visitor_check_ins']
        
        for table in tables:
            try:
                # Reiniciar secuencia al máximo ID + 1
                result = db.session.execute(text(f"SELECT MAX(id) FROM {table}"))
                max_id = result.scalar() or 0
                db.session.execute(text(f"SELECT setval('{table}_id_seq', {max_id + 1}, false)"))
                print(f"Secuencia {table}_id_seq reiniciada a {max_id + 1}")
            except Exception as e:
                print(f"Error reiniciando secuencia para {table}: {e}")
        
        db.session.commit()

def migrate_data(sqlite_file='app.db'):
    """Migrar datos de SQLite a PostgreSQL"""
    
    if not os.path.exists(sqlite_file):
        print(f"Error: No se encuentra el archivo {sqlite_file}")
        return
    
    # Conectar a SQLite
    sqlite_conn = sqlite3.connect(sqlite_file)
    sqlite_conn.row_factory = sqlite3.Row
    cursor = sqlite_conn.cursor()
    
    with app.app_context():
        # Limpiar tablas existentes (opcional)
        print("Limpiando tablas existentes...")
        db.session.query(VisitorCheckIn).delete()
        db.session.query(Visitor).delete()
        db.session.query(Event).delete()
        db.session.query(User).delete()
        db.session.query(Kiosk).delete()
        db.session.commit()
        
        # Migrar kioscos
        print("Migrando kioscos...")
        cursor.execute("SELECT * FROM kiosks")
        kiosks = cursor.fetchall()
        for row in kiosks:
            kiosk_dict = dict(row)
            kiosk = Kiosk(
                id=kiosk_dict['id'],
                name=kiosk_dict['name'],
                location=kiosk_dict['location'],
                is_active=bool(kiosk_dict['is_active'])
            )
            db.session.add(kiosk)
        db.session.commit()
        print(f"  {len(kiosks)} kioscos migrados")
        
        # Migrar usuarios
        print("Migrando usuarios...")
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        for row in users:
            user_dict = dict(row)
            user = User(
                id=user_dict['id'],
                username=user_dict['username'],
                email=user_dict['email'],
                password_hash=user_dict['password_hash'],
                first_name=user_dict.get('first_name') or 'Usuario',
                last_name=user_dict.get('last_name') or 'Sistema',
                role=user_dict.get('role') or 'admin',
                is_active=bool(user_dict.get('is_active', 1))
            )
            db.session.add(user)
        db.session.commit()
        print(f"  {len(users)} usuarios migrados")
        
        # Migrar eventos
        print("Migrando eventos...")
        cursor.execute("SELECT * FROM events")
        events = cursor.fetchall()
        for row in events:
            event_dict = dict(row)
            event = Event(
                id=event_dict['id'],
                title=event_dict['title'],
                description=event_dict['description'],
                start_date=datetime.fromisoformat(event_dict['start_date']),
                end_date=datetime.fromisoformat(event_dict['end_date']),
                location=event_dict['location'],
                is_active=bool(event_dict['is_active']),
                image_url=event_dict.get('image_url')
            )
            db.session.add(event)
        db.session.commit()
        print(f"  {len(events)} eventos migrados")
        
        # Migrar visitantes
        print("Migrando visitantes...")
        cursor.execute("SELECT * FROM visitors")
        visitors = cursor.fetchall()
        for row in visitors:
            visitor_dict = dict(row)
            visitor = Visitor(
                id=visitor_dict['id'],
                name=visitor_dict['name'],
                email=visitor_dict['email'],
                phone=visitor_dict.get('phone', ''),
                registration_code=visitor_dict.get('registration_code'),
                created_at=datetime.fromisoformat(visitor_dict['created_at']) if visitor_dict.get('created_at') else datetime.utcnow()
            )
            db.session.add(visitor)
        db.session.commit()
        print(f"  {len(visitors)} visitantes migrados")
        
        # Migrar check-ins
        print("Migrando check-ins...")
        cursor.execute("SELECT * FROM visitor_check_ins")
        checkins = cursor.fetchall()
        for row in checkins:
            checkin_dict = dict(row)
            checkin = VisitorCheckIn(
                id=checkin_dict['id'],
                visitor_id=checkin_dict['visitor_id'],
                event_id=checkin_dict['event_id'],
                kiosk_id=checkin_dict['kiosk_id'],
                check_in_time=datetime.fromisoformat(checkin_dict['check_in_time']) if checkin_dict.get('check_in_time') else datetime.utcnow()
            )
            db.session.add(checkin)
        db.session.commit()
        print(f"  {len(checkins)} check-ins migrados")
        
        # Reiniciar secuencias
        print("\nReiniciando secuencias de PostgreSQL...")
        reset_sequences()
        
        print("\n✅ Migración completada exitosamente")
        
        # Mostrar resumen
        print("\nResumen de migración:")
        print(f"  Kioscos: {db.session.query(Kiosk).count()}")
        print(f"  Usuarios: {db.session.query(User).count()}")
        print(f"  Eventos: {db.session.query(Event).count()}")
        print(f"  Visitantes: {db.session.query(Visitor).count()}")
        print(f"  Check-ins: {db.session.query(VisitorCheckIn).count()}")
    
    sqlite_conn.close()

def test_connection():
    """Probar conexión a PostgreSQL"""
    with app.app_context():
        try:
            # Probar conexión
            result = db.session.execute(text('SELECT 1'))
            print("✅ Conexión a PostgreSQL exitosa")
            
            # Mostrar configuración
            print(f"Base de datos: {app.config['SQLALCHEMY_DATABASE_URI']}")
            
            return True
        except Exception as e:
            print(f"❌ Error conectando a PostgreSQL: {e}")
            return False

if __name__ == "__main__":
    print("=== Migración SQLite → PostgreSQL ===\n")
    
    # Probar conexión primero
    if not test_connection():
        print("\nPor favor verifica tu configuración de PostgreSQL")
        sys.exit(1)
    
    # Preguntar confirmación
    print("\n⚠️  ADVERTENCIA: Esto sobrescribirá todos los datos en PostgreSQL")
    response = input("¿Deseas continuar? (s/n): ")
    
    if response.lower() == 's':
        migrate_data()
    else:
        print("Migración cancelada")
