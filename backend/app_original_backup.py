from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/api/v1/auth/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    if not username or not password:
        return jsonify({"error": "Nombre de usuario y contraseña son requeridos"}), 400
    if username != "admin" or password != "Admin123!":
        return jsonify({"error": "Credenciales incorrectas"}), 401
    return jsonify({
        "access_token": "token-de-ejemplo",
        "refresh_token": "refresh-token-ejemplo",
        "user": {
            "id": 2,
            "username": "admin",
            "email": "admin@ccb.do",
            "first_name": "Administrador",
            "last_name": "Sistema",
            "role": "admin",
            "is_active": True
        }
    })

@app.route("/api/v1/events/", methods=["GET"])
def get_events():
    return jsonify([
        {
            "id": 1,
            "title": "Recital de Poesía",
            "description": "Lectura de poemas",
            "start_date": "2025-05-20T18:00:00",
            "end_date": "2025-05-20T20:00:00",
            "location": "Sala de Conferencias",
            "is_active": True
        }
    ])

@app.route("/api/v1/events/<int:event_id>/visitors", methods=["POST"])
def register_visitor(event_id):
    # Aquí procesaríamos los datos del visitante
    visitor_data = request.json
    print(f"Registrando visitante para evento {event_id}: {visitor_data}")
    
    # Simular respuesta exitosa
    return jsonify({
        "success": True,
        "message": "Visitante registrado exitosamente",
        "visitor": visitor_data
    })

if __name__ == "__main__":
    app.run(port=8080, debug=True)
