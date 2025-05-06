"""
Script para gestionar migraciones de base de datos
"""
from flask import Flask
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from models.database import db
import models  # Importar todos los modelos

app = Flask(__name__)
app.config.from_pyfile('config/config.py')

db.init_app(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
