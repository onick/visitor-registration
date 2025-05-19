"""
Patch para agregar endpoints faltantes para la gestión de visitantes en eventos
"""

# Agregar después de los otros endpoints de visitantes

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
