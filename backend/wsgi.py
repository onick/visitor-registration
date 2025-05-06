"""
Punto de entrada WSGI para la aplicación
"""
from app import create_app

# Crear la aplicación
application = create_app()

# Para ejecutar con Gunicorn
if __name__ == "__main__":
    application.run() 