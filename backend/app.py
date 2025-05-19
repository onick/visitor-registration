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
from api.dashboard_analytics import init_dashboard_analytics
from api.export_endpoint import export_bp
from api.upload_endpoint import upload_bp
from api.visitors_api import visitors_bp
from flask import send_from_directory

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
    
    return app

app = create_app()

# Inicializar endpoints de analytics
init_dashboard_analytics(app)

# Registrar blueprint de exportación
app.register_blueprint(export_bp)

# Registrar blueprint de uploads
app.register_blueprint(upload_bp)

# Registrar blueprint de API de visitantes avanzada
app.register_blueprint(visitors_bp)

# ========================
# RUTA DE ARCHIVOS ESTÁTICOS
# ========================
@app.route('/uploads/<path:folder>/<path:filename>')
def serve_upload(folder, filename):
    """Servir archivos subidos"""
    upload_path = os.path.join(os.getcwd(), 'backend', 'uploads', folder)
    return send_from_directory(upload_path, filename)

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
        
        # Validar formatos de fecha
        try:
            start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
        except ValueError as e:
            return jsonify({"error": f"Formato de fecha inválido: {str(e)}"}), 400
        
        # Validar que la fecha de inicio sea anterior a la de fin
        if start_date >= end_date:
            return jsonify({"error": "La fecha de inicio debe ser anterior a la fecha de finalización"}), 400
        
        # Crear evento (sin campo type que causa el error)
        event = Event(
            title=data['title'],
            description=data['description'],
            start_date=start_date,
            end_date=end_date,
            location=data['location'],
            image_url=data.get('image_url'),
            is_active=data.get('is_active', True)
        )
        
        # Opcionales: capacity
        if 'capacity' in data and data['capacity'] is not None:
            try:
                capacity = int(data['capacity'])
                if capacity < 0:
                    return jsonify({"error": "La capacidad debe ser un número positivo"}), 400
                # Guardar capacidad en un campo personalizado (como no existe en el modelo)
                event.capacity = capacity
            except (ValueError, TypeError):
                return jsonify({"error": "El formato de capacidad es inválido"}), 400
        
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
        print(f"Error al crear evento: {str(e)}")
        import traceback
        traceback.print_exc()
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
        
        # Query base con join a VisitorCheckIn y Event
        query = db.session.query(
            Visitor,
            VisitorCheckIn,
            Event
        ).join(
            VisitorCheckIn, 
            Visitor.id == VisitorCheckIn.visitor_id,
            isouter=True
        ).join(
            Event,
            VisitorCheckIn.event_id == Event.id,
            isouter=True
        )
        
        # Filtrar por búsqueda
        if search:
            query = query.filter(
                db.or_(
                    Visitor.name.contains(search),
                    Visitor.email.contains(search),
                    Visitor.phone.contains(search),
                    Visitor.registration_code.contains(search)
                )
            )
        
        # Filtrar por evento
        if event_id:
            query = query.filter(VisitorCheckIn.event_id == event_id)
        
        # Obtener resultados únicos
        results = query.distinct().all()
        
        # Paginar manualmente los resultados
        start = (page - 1) * limit
        end = start + limit
        total = len(results)
        paginated_results = results[start:end]
        
        visitors_data = []
        for visitor, checkin, event in paginated_results:
            visitor_info = {
                "id": visitor.id,
                "name": visitor.name,
                "email": visitor.email,
                "phone": visitor.phone,
                "registration_code": visitor.registration_code,
                "created_at": visitor.created_at.isoformat() if visitor.created_at else None,
                "check_ins_count": len(visitor.check_ins),
                "event": None,
                "event_title": None,
                "checked_in": False,
                "check_in_time": None
            }
            
            # Agregar información del evento si existe
            if event:
                visitor_info["event"] = {
                    "id": event.id,
                    "title": event.title,
                    "start_date": event.start_date.isoformat() if event.start_date else None,
                    "end_date": event.end_date.isoformat() if event.end_date else None,
                    "location": event.location
                }
                visitor_info["event_title"] = event.title
                visitor_info["checked_in"] = checkin is not None
                visitor_info["check_in_time"] = checkin.check_in_time.isoformat() if checkin and checkin.check_in_time else None
            
            visitors_data.append(visitor_info)
        
        return jsonify({
            "items": visitors_data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit  # División entera redondeada hacia arriba
            }
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
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
            print(f"Nuevo visitante creado: {visitor.name}, código: '{visitor.registration_code}'")
        else:
            print(f"Visitante existente: {visitor.name}, código: '{visitor.registration_code}'")
        
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
        
        print(f"Registro completado - Código: '{visitor.registration_code}'")
        
        return jsonify({
            "success": True,
            "message": "Visitante registrado exitosamente",
            "visitor_id": visitor.id,
            "registration_code": visitor.registration_code,
            "checkin_id": checkin.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error en registro: {str(e)}")
        import traceback
        traceback.print_exc()
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
        
        # Limpiar el código (quitar espacios)
        code = code.strip()
        
        print(f"Verificando código: '{code}' (longitud: {len(code)})")
        
        # Buscar visitante por código, email, teléfono o ID
        visitor = None
        
        # Primero intentar buscar por código de registro (exacto)
        visitor = Visitor.query.filter_by(registration_code=code).first()
        print(f"Búsqueda por código exacto: {'Encontrado' if visitor else 'No encontrado'}")
        
        if not visitor:
            # Intentar buscar por código en mayúsculas
            visitor = Visitor.query.filter_by(registration_code=code.upper()).first()
            print(f"Búsqueda por código en mayúsculas: {'Encontrado' if visitor else 'No encontrado'}")
        
        if not visitor:
            # Intentar buscar por ID numérico
            try:
                visitor_id = int(code)
                visitor = Visitor.query.get(visitor_id)
                print(f"Búsqueda por ID {visitor_id}: {'Encontrado' if visitor else 'No encontrado'}")
            except ValueError:
                # Si no es un número, buscar por email o teléfono
                visitor = Visitor.query.filter(
                    db.or_(
                        Visitor.email == code,
                        Visitor.phone == code
                    )
                ).first()
                print(f"Búsqueda por email/teléfono: {'Encontrado' if visitor else 'No encontrado'}")
        
        if not visitor:
            # Log para debug
            print(f"No se encontró visitante con código: '{code}'")
            # Mostrar algunos códigos existentes para debug (solo en desarrollo)
            if app.debug:
                sample_visitors = Visitor.query.limit(3).all()
                print("Ejemplos de códigos existentes:")
                for v in sample_visitors:
                    print(f"  - {v.name}: '{v.registration_code}'")
            
            return jsonify({"error": "Código no válido"}), 404
        
        print(f"Visitante encontrado: {visitor.name} (ID: {visitor.id})")
        
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
            Event.is_active == True
        ).all()
        
        # Si no hay filtro por fechas, mostrar todos los eventos del visitante
        if not active_registrations:
            active_registrations = db.session.query(
                VisitorCheckIn,
                Event
            ).join(
                Event, 
                VisitorCheckIn.event_id == Event.id
            ).filter(
                VisitorCheckIn.visitor_id == visitor.id
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
                "phone": visitor.phone,
                "registration_code": visitor.registration_code
            },
            "events": events_data
        })
        
    except Exception as e:
        print(f"Error en verify-code: {str(e)}")
        import traceback
        traceback.print_exc()
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
