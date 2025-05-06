"""
Script para migraciones de base de datos
"""
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from app import create_app
from models.database import db
from models.event import Event
from models.visitor import Visitor, VisitorCheckIn
from models.kiosk import Kiosk, KioskConfig
from models.user import User

app = create_app()
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

@manager.command
def create_tables():
    """
    Crear tablas de base de datos
    """
    with app.app_context():
        db.create_all()

@manager.command
def drop_tables():
    """
    Eliminar tablas de base de datos
    """
    with app.app_context():
        db.drop_all()

if __name__ == '__main__':
    manager.run()
