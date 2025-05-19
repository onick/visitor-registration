"""
Aplicación Flask mejorada con SQLAlchemy y endpoints completos
"""
import os
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from models.database import db, init_app
from models.visitor import Visitor, VisitorCheckIn
from models.event import Event
from models.user import User
from models.kiosk import Kiosk

def create_app():
    """Crear y configurar la aplicación Flask"""
    app = Flask(__name__)
    
    # Configuración
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dev.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    
    # Inicializar extensiones
    CORS(app)
    init_app(app)
    
    return app

app = create_app()

# ========================
# ENDPOINTS DE AUTENTICACIÓN
# ========================
@app.route("/api/v1/auth/login", methods=["POST"])
def login():
    """Endpoint de login simplificado"""
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    
    if not username or not password:
        return jsonify({"error": "Nombre de usuario y contraseña son requeridos"}), 400
    
    # TODO: Implementar autenticación real con JWT
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

# ========================
# ENDPOINTS DE EVENTOS
# ========================
@app.route("/api/v1/events/", methods=["GET"])
def get_events():
    """Obtener lista de eventos"""
    try:
        events = Event.query.all()
        
        events_data = []
        for event in events:
            events_data.append({
                "id": event.id,
                "title": event.title,
                "description": event.description,
                "start_date": event.start_date.isoformat() if event.start_date else None,
                "end_date": event.end_date.isoformat() if event.end_date else None,
                "location": event.location,
                "image_url": event.image_url,
                "is_active": event.is_active,
                "is_ongoing": event.is_ongoing
            })
        
        return jsonify(events_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/events/<int:event_id>", methods=["GET"])
def get_event_by_id(event_id):
    """Obtener un evento específico"""
    try:
        event = Event.query.get_or_404(event_id)
        
        return jsonify({
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "start_date": event.start_date.isoformat() if event.start_date else None,
            "end_date": event.end_date.isoformat() if event.end_date else None,
            "location": event.location,
            "image_url": event.image_url,
            "is_active": event.is_active,
            "is_ongoing": event.is_ongoing,
            "visitors_count": len(event.visitors)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ========================
# ENDPOINTS DE VISITANTES
# ========================
@app.route("/api/v1/visitors", methods=["GET"])
def get_visitors():
    """Obtener lista de visitantes con paginación"""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        search = request.args.get('search', '', type=str)
        event_id = request.args.get('event_id', type=int)
        
        query = Visitor.query
        
        # Filtrar por búsqueda
        if search:
            query = query.filter(
                db.or_(
                    Visitor.name.contains(search),
                    Visitor.email.contains(search),
                    Visitor.phone.contains(search)
                )
            )
        
        # Filtrar por evento
        if event_id:
            query = query.join(VisitorCheckIn).filter(VisitorCheckIn.event_id == event_id)
        
        # Paginar resultados
        pagination = query.paginate(page=page, per_page=limit, error_out=False)
        
        visitors_data = []
        for visitor in pagination.items:
            visitors_data.append({
                "id": visitor.id,
                "name": visitor.name,
                "email": visitor.email,
                "phone": visitor.phone,
                "created_at": visitor.created_at.isoformat() if visitor.created_at else None,
                "check_ins_count": len(visitor.check_ins)
            })
        
        return jsonify({
            "items": visitors_data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": pagination.total,
                "pages": pagination.pages
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/visitors/register", methods=["POST"])
def register_visitor():
    """Registrar un nuevo visitante para un evento"""
    try:
        data = request.json
        
        # Validar datos requeridos
        required_fields = ['name', 'email', 'event_id']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Campo '{field}' es requerido"}), 400
        
        # Buscar o crear visitante
        visitor = Visitor.query.filter_by(email=data['email']).first()
        if not visitor:
            visitor = Visitor(
                name=data['name'],
                email=data['email'],
                phone=data.get('phone', '')
            )
            db.session.add(visitor)
            db.session.flush()
        
        # Verificar si ya está registrado para este evento
        existing_checkin = VisitorCheckIn.query.filter_by(
            visitor_id=visitor.id,
            event_id=data['event_id']
        ).first()
        
        if existing_checkin:
            return jsonify({
                "error": "El visitante ya está registrado para este evento"
            }), 400
        
        # Crear registro de check-in
        checkin = VisitorCheckIn(
            visitor_id=visitor.id,
            event_id=data['event_id'],
            kiosk_id=data.get('kiosk_id', 1)  # Default kiosk_id = 1
        )
        db.session.add(checkin)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Visitante registrado exitosamente",
            "visitor_id": visitor.id,
            "checkin_id": checkin.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/visitors/statistics", methods=["GET"])
def get_visitor_statistics():
    """Obtener estadísticas de visitantes"""
    try:
        # Total de visitantes
        total_visitors = Visitor.query.count()
        
        # Visitantes hoy
        today = datetime.utcnow().date()
        today_visitors = db.session.query(VisitorCheckIn).filter(
            db.func.date(VisitorCheckIn.check_in_time) == today
        ).count()
        
        # Total de check-ins
        total_checkins = VisitorCheckIn.query.count()
        
        # Estadísticas por evento
        events_stats = db.session.query(
            Event.id,
            Event.title,
            db.func.count(VisitorCheckIn.id).label('visitors_count')
        ).join(VisitorCheckIn).group_by(Event.id).all()
        
        events_data = []
        for event_id, event_title, count in events_stats:
            events_data.append({
                "event_id": event_id,
                "event_title": event_title,
                "visitors_count": count
            })
        
        return jsonify({
            "total": total_visitors,
            "today": today_visitors,
            "checkedIn": total_checkins,
            "by_event": events_data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/events/<int:event_id>/visitors", methods=["POST"])
def register_visitor_for_event(event_id):
    """Registrar visitante para un evento específico"""
    try:
        data = request.json
        data['event_id'] = event_id  # Agregar event_id a los datos
        
        # Reutilizar la función de registro
        request.json = data
        return register_visitor()
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ========================
# ENDPOINTS DE CHECK-IN
# ========================
@app.route("/api/v1/events/<int:event_id>/visitors/<int:visitor_id>/checkin", methods=["POST"])
def checkin_visitor(event_id, visitor_id):
    """Hacer check-in de un visitante para un evento"""
    try:
        # Verificar que existe el registro
        checkin = VisitorCheckIn.query.filter_by(
            visitor_id=visitor_id,
            event_id=event_id
        ).first()
        
        if not checkin:
            return jsonify({"error": "Visitante no está registrado para este evento"}), 404
        
        # Actualizar tiempo de check-in
        checkin.check_in_time = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Check-in realizado exitosamente",
            "check_in_time": checkin.check_in_time.isoformat()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# ========================
# INICIALIZACIÓN
# ========================
@app.before_first_request
def create_tables():
    """Crear tablas si no existen"""
    db.create_all()
    
    # Crear evento de prueba si no hay eventos
    if Event.query.count() == 0:
        event = Event(
            title="Recital de Poesía",
            description="Lectura de poemas de autores dominicanos",
            start_date=datetime(2025, 5, 20, 18, 0),
            end_date=datetime(2025, 5, 20, 20, 0),
            location="Sala de Conferencias",
            is_active=True
        )
        db.session.add(event)
        db.session.commit()
        print("Evento de prueba creado")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
