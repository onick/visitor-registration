from flask import Flask
import os
import sys
import json

# Agregar la ruta actual al PATH para que podamos importar módulos locales
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar la función de creación de app y los modelos necesarios
try:
    from app import create_app
    from models.database import db
    from models.user import User
    
    # Crear la aplicación en modo de prueba
    app = create_app()
    
    with app.app_context():
        # Obtener el primer usuario
        user = User.query.first()
        
        if user:
            # Obtener el diccionario del usuario e imprimirlo para ver su formato
            user_dict = user.to_dict()
            print("Formato del objeto usuario:")
            print(json.dumps(user_dict, indent=2))
            
            # Verificar si existe el campo firstName
            print("\nVerificación de campos:")
            print(f"- Tiene first_name: {'first_name' in user_dict}")
            print(f"- Tiene firstName: {'firstName' in user_dict}")
            print(f"- Tiene last_name: {'last_name' in user_dict}")
            print(f"- Tiene lastName: {'lastName' in user_dict}")
        else:
            print("No se encontró ningún usuario en la base de datos.")
except Exception as e:
    print(f"Error al verificar el formato de usuario: {str(e)}") 