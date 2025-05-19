"""
Aplicación Flask mejorada con soporte para múltiples bases de datos
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
from config.database_config import config
from dotenv import load_dotenv
from api.visitors_api import visitors_bp

# Cargar variables de entorno
load_dotenv()

def create_app(config_name=None):
    """Crear y configurar la aplicación Flask"""
    app = Flask(__name__)
    
    # Seleccionar configuración basada en el ambiente
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # Sobrescribir con DATABASE_URL si está presente en el entorno
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    
    # Inicializar extensiones
    CORS(app)
    init_app(app)
    
    # Registrar blueprints
    app.register_blueprint(visitors_bp)
    
    return app

app = create_app()

# ========================
# RUTA DE INICIO
# ========================
@app.route("/")
def index():
    """Página de inicio del API"""
    return jsonify({
        "message": "API del Sistema de Registro de Visitantes CCB",
        "version": "1.0",
        "endpoints": {
            "auth": "/api/v1/auth/login",
            "events": "/api/v1/events/",
            "visitors": "/api/v1/visitors",
            "statistics": "/api/v1/visitors/statistics"
        },
        "status": "online",
        "database": "PostgreSQL"
    })

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
            # Obtener número de visitantes registrados
            registered_count = VisitorCheckIn.query.filter_by(event_id=event.id).count()
            
            events_data.append({
                "id": event.id,
                "title": event.title,
                "description": event.description,
                "start_date": event.start_date.isoformat() if event.start_date else None,
                "end_date": event.end_date.isoformat() if event.end_date else None,
                "location": event.location,
                "image_url": event.image_url,
                "is_active": event.is_active,
                "is_ongoing": event.is_ongoing,
                "registered_count": registered_count,
                "checked_in_count": registered_count  # Por ahora, todos los registrados se consideran con check-in
            })
        
        return jsonify(events_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/events/<int:event_id>", methods=["GET"])
def get_event_by_id(event_id):
    """Obtener un evento específico"""
    try:
        event = Event.query.get_or_404(event_id)
        
        # Obtener número de visitantes registrados
        registered_count = VisitorCheckIn.query.filter_by(event_id=event_id).count()
        
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
            "visitors_count": len(event.visitors),
            "registered_count": registered_count,
            "checked_in_count": registered_count  # Por ahora, todos los registrados se consideran con check-in
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/events/", methods=["POST"])
def create_event():
    """Crear un nuevo evento"""
    try:
        data = request.json
        
        # Validar datos requeridos
        required_fields = ['title', 'description', 'start_date', 'end_date', 'location']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Campo '{field}' es requerido"}), 400
        
        # Crear evento (sin el campo type)
        event = Event(
            title=data['title'],
            description=data['description'],
            start_date=datetime.fromisoformat(data['start_date'].replace('Z', '+00:00')),
            end_date=datetime.fromisoformat(data['end_date'].replace('Z', '+00:00')),
            location=data['location'],
            image_url=data.get('image_url'),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(event)
        db.session.commit()
        
        return jsonify({
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "start_date": event.start_date.isoformat() if event.start_date else None,
            "end_date": event.end_date.isoformat() if event.end_date else None,
            "location": event.location,
            "image_url": event.image_url,
            "is_active": event.is_active
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/events/<int:event_id>/", methods=["PUT"])
def update_event(event_id):
    """Actualizar un evento existente"""
    try:
        event = Event.query.get_or_404(event_id)
        data = request.json
        
        # Actualizar campos si están presentes
        if 'title' in data:
            event.title = data['title']
        if 'description' in data:
            event.description = data['description']
        if 'start_date' in data:
            event.start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
        if 'end_date' in data:
            event.end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
        if 'location' in data:
            event.location = data['location']
        if 'image_url' in data:
            event.image_url = data['image_url']
        if 'is_active' in data:
            event.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "start_date": event.start_date.isoformat() if event.start_date else None,
            "end_date": event.end_date.isoformat() if event.end_date else None,
            "location": event.location,
            "image_url": event.image_url,
            "is_active": event.is_active
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/events/<int:event_id>/", methods=["DELETE"])
def delete_event(event_id):
    """Eliminar un evento"""
    try:
        event = Event.query.get_or_404(event_id)
        
        # Eliminar registros relacionados primero
        VisitorCheckIn.query.filter_by(event_id=event_id).delete()
        
        # Eliminar el evento
        db.session.delete(event)
        db.session.commit()
        
        return '', 204
        
    except Exception as e:
        db.session.rollback()
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
            "registration_code": visitor.registration_code,
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
@app.route("/api/v1/visitors/verify-code", methods=["POST"])
def verify_visitor_code():
    """Verificar código de visitante para check-in rápido"""
    try:
        data = request.json
        code = data.get('code')
        
        if not code:
            return jsonify({"error": "Código es requerido"}), 400
        
        # Buscar visitante por código, email, teléfono o ID
        visitor = None
        
        # Primero intentar buscar por código de registro
        visitor = Visitor.query.filter_by(registration_code=code.upper()).first()
        
        if not visitor:
            # Intentar buscar por ID numérico
            try:
                visitor_id = int(code)
                visitor = Visitor.query.get(visitor_id)
            except ValueError:
                # Si no es un número, buscar por email o teléfono
                visitor = Visitor.query.filter(
                    db.or_(
                        Visitor.email == code,
                        Visitor.phone == code
                    )
                ).first()
        
        if not visitor:
            return jsonify({"error": "Código no válido"}), 404
        
        # Obtener eventos activos del visitante
        now = datetime.utcnow()
        active_registrations = db.session.query(
            VisitorCheckIn,
            Event
        ).join(
            Event, 
            VisitorCheckIn.event_id == Event.id
        ).filter(
            VisitorCheckIn.visitor_id == visitor.id,
            Event.is_active == True,
            Event.start_date <= now,
            Event.end_date >= now
        ).all()
        
        events_data = []
        for registration, event in active_registrations:
            events_data.append({
                "id": event.id,
                "title": event.title,
                "start_date": event.start_date.isoformat() if event.start_date else None,
                "end_date": event.end_date.isoformat() if event.end_date else None,
                "location": event.location,
                "registration_id": registration.id,
                "checked_in": registration.check_in_time is not None
            })
        
        return jsonify({
            "visitor": {
                "id": visitor.id,
                "name": visitor.name,
                "email": visitor.email,
                "phone": visitor.phone
            },
            "events": events_data
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ========================
# ENDPOINTS ADICIONALES DE VISITANTES EN EVENTOS
# ========================
@app.route("/api/v1/visitors/event/<int:event_id>", methods=["GET"])
def get_event_visitors(event_id):
    """Obtener visitantes registrados para un evento específico"""
    try:
        # Verificar que el evento existe
        event = Event.query.get_or_404(event_id)
        
        # Obtener visitantes del evento a través de VisitorCheckIn
        visitors_with_checkins = db.session.query(
            Visitor,
            VisitorCheckIn
        ).join(
            VisitorCheckIn, 
            Visitor.id == VisitorCheckIn.visitor_id
        ).filter(
            VisitorCheckIn.event_id == event_id
        ).all()
        
        visitors_data = []
        for visitor, checkin in visitors_with_checkins:
            visitors_data.append({
                "id": visitor.id,
                "name": visitor.name,
                "email": visitor.email,
                "phone": visitor.phone,
                "registered_at": checkin.check_in_time.isoformat() if checkin.check_in_time else None,
                "checked_in": True,  # Por ahora, todos se consideran con check-in
                "kiosk_id": checkin.kiosk_id
            })
        
        return jsonify(visitors_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/events/<int:event_id>/export", methods=["GET"])
def export_event_data(event_id):
    """Exportar datos de visitantes de un evento"""
    try:
        # Verificar que el evento existe
        event = Event.query.get_or_404(event_id)
        
        # Obtener formato de exportación
        export_format = request.args.get('format', 'csv')
        
        # Obtener visitantes del evento
        visitors_with_checkins = db.session.query(
            Visitor,
            VisitorCheckIn
        ).join(
            VisitorCheckIn, 
            Visitor.id == VisitorCheckIn.visitor_id
        ).filter(
            VisitorCheckIn.event_id == event_id
        ).all()
        
        # Por ahora, solo devolver los datos en JSON
        # TODO: Implementar exportación real a CSV/Excel
        
        visitors_data = []
        for visitor, checkin in visitors_with_checkins:
            visitors_data.append({
                "id": visitor.id,
                "name": visitor.name,
                "email": visitor.email,
                "phone": visitor.phone,
                "check_in_time": checkin.check_in_time.isoformat() if checkin.check_in_time else None,
                "kiosk_id": checkin.kiosk_id
            })
        
        return jsonify({
            "event": {
                "id": event.id,
                "title": event.title,
                "location": event.location
            },
            "visitors": visitors_data,
            "format": export_format
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/events/<int:event_id>/statistics", methods=["GET"])
def get_event_statistics(event_id):
    """Obtener estadísticas de un evento específico"""
    try:
        # Verificar que el evento existe
        event = Event.query.get_or_404(event_id)
        
        # Obtener número de visitantes registrados
        registered_count = VisitorCheckIn.query.filter_by(event_id=event_id).count()
        
        # Por ahora, todos los registrados se consideran con check-in
        checked_in_count = registered_count
        
        return jsonify({
            "event_id": event_id,
            "event_title": event.title,
            "registered": registered_count,
            "checked_in": checked_in_count,
            "attendance_rate": (checked_in_count / registered_count * 100) if registered_count > 0 else 0
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ========================
# INICIALIZACIÓN
# ========================
def init_db():
    """Inicializar base de datos con datos de prueba"""
    with app.app_context():
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
    init_db()  # Inicializar base de datos
    app.run(host='0.0.0.0', port=8080, debug=True)
