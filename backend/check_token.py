from flask import Flask
from flask_jwt_extended import JWTManager, decode_token
import sys

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'super-secret-key-for-development-only'
jwt = JWTManager(app)

def check_token(token):
    with app.app_context():
        try:
            decoded = decode_token(token)
            print("Token decodificado:")
            print(decoded)
            
            if 'role' in decoded:
                print(f"Rol encontrado: {decoded['role']}")
            else:
                print("No se encontró el rol en el token")
                
            return decoded
        except Exception as e:
            print(f"Error al decodificar el token: {e}")
            return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        token = sys.argv[1]
        check_token(token)
    else:
        print("Por favor proporcione un token JWT como argumento") 