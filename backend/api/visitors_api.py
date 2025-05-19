"""
Endpoints para la gestión avanzada de visitantes
"""
from flask import Blueprint, jsonify, request
import json
from datetime import datetime
from sqlalchemy import func
from models.database import db
from models.visitor import Visitor, VisitorCheckIn
from models.event import Event
from models.kiosk import Kiosk
from services.email_service import send_invitation_email

visitors_bp = Blueprint('visitors_api', __name__)

@visitors_bp.route("/api/v1/visitors/summary", methods=["GET"])
def get_visitors_summary():
    """
    Endpoint para obtener un resumen de los visitantes con sus últimos eventos e intereses
    """
    try:
        # Obtener todos los visitantes
        visitors = Visitor.query.all()
        
        # Preparar los datos de resumen
        summary_data = []
        
        for visitor in visitors:
            # Obtener el último evento al que asistió
            last_checkin = VisitorCheckIn.query.filter_by(
                visitor_id=visitor.id
            ).order_by(VisitorCheckIn.check_in_time.desc()).first()
            
            last_event = None
            if last_checkin:
                event = Event.query.get(last_checkin.event_id)
                if event:
                    last_event = {
                        "title": event.title,
                        "type": event.type,
                        "date": last_checkin.check_in_time.isoformat()
                    }
            
            # Obtener intereses
            interests = visitor.get_interests()
            
            # Obtener estadísticas de visitas por tipo
            visit_stats = {}
            event_types = db.session.query(Event.type).join(
                VisitorCheckIn,
                VisitorCheckIn.event_id == Event.id
            ).filter(
                VisitorCheckIn.visitor_id == visitor.id
            ).group_by(Event.type).all()
            
            for event_type in event_types:
                type_name = event_type[0]
                visit_count = db.session.query(VisitorCheckIn).join(
                    Event,
                    VisitorCheckIn.event_id == Event.id
                ).filter(
                    VisitorCheckIn.visitor_id == visitor.id,
                    Event.type == type_name
                ).count()
                
                visit_stats[type_name] = visit_count
            
            # Crear el objeto de resumen para este visitante
            visitor_summary = {
                "id": visitor.id,
                "name": visitor.name,
                "email": visitor.email,
                "phone": visitor.phone,
                "code": visitor.registration_code,
                "last_event": last_event,
                "interests": interests,
                "total_visits": visit_stats
            }
            
            summary_data.append(visitor_summary)
        
        return jsonify(summary_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@visitors_bp.route("/api/v1/visitors", methods=["GET"])
def get_visitors_with_filters():
    """
    Endpoint para obtener visitantes con filtros adicionales por interés
    """
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        search = request.args.get('search', '', type=str)
        event_id = request.args.get('event_id', type=int)
        interest = request.args.get('interest', '', type=str)
        
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
        
        # Filtrar por interés
        if interest:
            # Filtrar visitantes que tengan el interés especificado
            query = query.filter(Visitor.interests.contains(interest))
        
        # Paginar resultados
        pagination = query.paginate(page=page, per_page=limit, error_out=False)
        
        visitors_data = []
        for visitor in pagination.items:
            # Obtener el último evento al que asistió
            last_checkin = VisitorCheckIn.query.filter_by(
                visitor_id=visitor.id
            ).order_by(VisitorCheckIn.check_in_time.desc()).first()
            
            last_event = None
            if last_checkin:
                event = Event.query.get(last_checkin.event_id)
                if event:
                    last_event = {
                        "id": event.id,
                        "title": event.title,
                        "type": event.type,
                        "date": last_checkin.check_in_time.isoformat()
                    }
            
            visitor_data = {
                "id": visitor.id,
                "name": visitor.name,
                "email": visitor.email,
                "phone": visitor.phone,
                "registration_code": visitor.registration_code,
                "created_at": visitor.created_at.isoformat() if visitor.created_at else None,
                "check_ins_count": len(visitor.check_ins),
                "interests": visitor.get_interests(),
                "last_event": last_event
            }
            
            visitors_data.append(visitor_data)
        
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

@visitors_bp.route("/api/v1/invitations/send", methods=["POST"])
def send_invitations():
    """
    Enviar invitaciones por correo a visitantes seleccionados
    """
    try:
        data = request.json
        
        visitor_ids = data.get('visitor_ids', [])
        event_type = data.get('event_type', '')
        event_id = data.get('event_id')
        
        if not visitor_ids:
            return jsonify({"error": "Se requiere una lista de IDs de visitantes"}), 400
        
        if not event_id:
            return jsonify({"error": "Se requiere el ID del evento"}), 400
        
        # Obtener el evento
        event = Event.query.get_or_404(event_id)
        
        # Obtener visitantes
        visitors = Visitor.query.filter(Visitor.id.in_(visitor_ids)).all()
        
        if not visitors:
            return jsonify({"error": "No se encontraron visitantes con los IDs proporcionados"}), 404
        
        # Enviar invitaciones
        results = []
        for visitor in visitors:
            # Verificar si el visitante ya está registrado para este evento
            existing_checkin = VisitorCheckIn.query.filter_by(
                visitor_id=visitor.id,
                event_id=event.id
            ).first()
            
            if existing_checkin:
                results.append({
                    "visitor_id": visitor.id,
                    "name": visitor.name,
                    "email": visitor.email,
                    "success": False,
                    "message": "El visitante ya está registrado para este evento"
                })
                continue
            
            # Enviar correo de invitación
            try:
                send_invitation_email(
                    visitor.email, 
                    visitor.name, 
                    event.type, 
                    event.title, 
                    visitor.registration_code
                )
                
                results.append({
                    "visitor_id": visitor.id,
                    "name": visitor.name,
                    "email": visitor.email,
                    "success": True,
                    "message": "Invitación enviada exitosamente"
                })
            except Exception as e:
                results.append({
                    "visitor_id": visitor.id,
                    "name": visitor.name,
                    "email": visitor.email,
                    "success": False,
                    "message": f"Error al enviar invitación: {str(e)}"
                })
        
        return jsonify({
            "success": True,
            "message": f"Proceso de envío completado. {sum(1 for r in results if r['success'])} de {len(results)} invitaciones enviadas.",
            "results": results
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
