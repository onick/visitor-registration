"""
Endpoints para la gestión de visitantes
"""
from flask_restx import Namespace, Resource, fields
from flask import request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.visitor import Visitor, VisitorCheckIn
from models.event import Event
from models.kiosk import Kiosk
from models.database import db
from datetime import datetime, date, timedelta
from utils.validators import validate_required_fields, validate_visitor_data
from utils.decorators import role_required
from sqlalchemy import func, desc, or_
import csv
import io
import xlsxwriter

visitors_namespace = Namespace('visitors', description='Operaciones relacionadas con visitantes')

# Modelos para la documentación de la API
visitor_model = visitors_namespace.model('Visitor', {
    'id': fields.Integer(readonly=True, description='Identificador único del visitante'),
    'name': fields.String(required=True, description='Nombre del visitante'),
    'email': fields.String(description='Correo electrónico del visitante'),
    'phone': fields.String(description='Teléfono del visitante'),
    'created_at': fields.DateTime(readonly=True, description='Fecha de registro')
})

# Modelo para respuesta paginada
pagination_model = visitors_namespace.model('PaginatedResponse', {
    'items': fields.List(fields.Nested(visitor_model), description='Lista de elementos'),
    'page': fields.Integer(description='Página actual'),
    'per_page': fields.Integer(description='Elementos por página'),
    'total_pages': fields.Integer(description='Total de páginas'),
    'total_items': fields.Integer(description='Total de elementos')
})

visitor_check_in_model = visitors_namespace.model('VisitorCheckIn', {
    'visitor_id': fields.Integer(required=True, description='ID del visitante'),
    'event_id': fields.Integer(required=True, description='ID del evento'),
    'kiosk_id': fields.Integer(required=True, description='ID del kiosco'),
    'check_in_time': fields.DateTime(readonly=True, description='Tiempo de registro')
})

# Modelo para la creación de visitantes y registro en un evento
visitor_registration_model = visitors_namespace.model('VisitorRegistration', {
    'name': fields.String(required=True, description='Nombre del visitante'),
    'email': fields.String(description='Correo electrónico del visitante'),
    'phone': fields.String(description='Teléfono del visitante'),
    'event_id': fields.Integer(required=True, description='ID del evento'),
    'kiosk_id': fields.Integer(required=True, description='ID del kiosco')
})

# Modelo para estadísticas
visitor_stats_model = visitors_namespace.model('VisitorStats', {
    'total_visitors': fields.Integer(description='Total de visitantes registrados'),
    'total_check_ins': fields.Integer(description='Total de check-ins'),
    'visitors_today': fields.Integer(description='Visitantes registrados hoy'),
    'check_ins_today': fields.Integer(description='Check-ins realizados hoy'),
    'most_popular_event': fields.Nested(visitors_namespace.model('PopularEvent', {
        'id': fields.Integer(description='ID del evento'),
        'title': fields.String(description='Título del evento'),
        'count': fields.Integer(description='Cantidad de visitantes')
    }))
})

@visitors_namespace.route('/')
class VisitorList(Resource):
    """
    Operaciones para lista de visitantes
    """
    @visitors_namespace.doc('list_visitors', security='apikey', params={
        'page': 'Número de página (por defecto: 1)',
        'per_page': 'Elementos por página (por defecto: 20, máximo: 100)',
        'search': 'Término de búsqueda en nombre o email',
        'event_id': 'Filtrar por ID de evento',
        'start_date': 'Filtrar desde fecha (YYYY-MM-DD)',
        'end_date': 'Filtrar hasta fecha (YYYY-MM-DD)',
        'has_check_in': 'Filtrar por estado de check-in (true/false)'
    })
    @visitors_namespace.marshal_with(pagination_model)
    @jwt_required()
    @role_required(['admin', 'staff'])
    def get(self):
        """
        Obtener lista paginada de visitantes con filtros
        """
        # Parámetros de paginación
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)  # Limitar a máximo 100 elementos
        
        # Parámetros de filtrado
        search_term = request.args.get('search', '')
        event_id = request.args.get('event_id', type=int)
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        has_check_in = request.args.get('has_check_in')
        
        # Construir consulta base
        query = Visitor.query
        
        # Aplicar filtros
        if search_term:
            query = query.filter(or_(
                Visitor.name.ilike(f'%{search_term}%'),
                Visitor.email.ilike(f'%{search_term}%')
            ))
        
        if event_id:
            # Subconsulta para visitantes que tienen check-in en el evento
            visitor_ids_with_checkin = db.session.query(VisitorCheckIn.visitor_id).filter_by(event_id=event_id).subquery()
            query = query.filter(Visitor.id.in_(visitor_ids_with_checkin))
        
        # Filtrar por fechas
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                query = query.filter(func.date(Visitor.created_at) >= start_date)
            except ValueError:
                pass  # Ignorar si el formato de fecha es incorrecto
        
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                query = query.filter(func.date(Visitor.created_at) <= end_date)
            except ValueError:
                pass  # Ignorar si el formato de fecha es incorrecto
        
        # Filtrar por estado de check-in (si se especifica)
        if has_check_in is not None:
            has_check_in = has_check_in.lower() == 'true'
            if has_check_in:
                # Visitantes que tienen al menos un check-in
                visitor_ids_with_checkin = db.session.query(VisitorCheckIn.visitor_id).distinct().subquery()
                query = query.filter(Visitor.id.in_(visitor_ids_with_checkin))
            else:
                # Visitantes que no tienen check-in
                visitor_ids_with_checkin = db.session.query(VisitorCheckIn.visitor_id).distinct().subquery()
                query = query.filter(~Visitor.id.in_(visitor_ids_with_checkin))
        
        # Ejecutar consulta paginada
        paginated_visitors = query.order_by(desc(Visitor.created_at)).paginate(page=page, per_page=per_page)
        
        # Preparar respuesta
        response = {
            'items': paginated_visitors.items,
            'page': paginated_visitors.page,
            'per_page': paginated_visitors.per_page,
            'total_pages': paginated_visitors.pages,
            'total_items': paginated_visitors.total
        }
        
        return response
    
    @visitors_namespace.doc('create_visitor', security='apikey')
    @visitors_namespace.expect(visitor_model)
    @visitors_namespace.marshal_with(visitor_model, code=201)
    @jwt_required()
    @role_required(['admin', 'staff'])
    @validate_required_fields(['name'])
    def post(self):
        """
        Registrar un nuevo visitante
        """
        # Implementación para crear un visitante
        data = request.json
        
        # Validar datos del visitante
        errors = validate_visitor_data(data)
        if errors:
            return {'errors': errors}, 400
        
        # Verificar si el visitante ya existe por email
        existing_visitor = None
        if 'email' in data and data['email']:
            existing_visitor = Visitor.query.filter_by(email=data['email']).first()
            
        if existing_visitor:
            return existing_visitor, 200
            
        # Crear nuevo visitante
        new_visitor = Visitor(
            name=data['name'],
            email=data.get('email'),
            phone=data.get('phone')
        )
        
        db.session.add(new_visitor)
        db.session.commit()
        
        return new_visitor, 201

@visitors_namespace.route('/<int:id>')
@visitors_namespace.param('id', 'Identificador del visitante')
class VisitorResource(Resource):
    """
    Operaciones para visitantes individuales
    """
    @visitors_namespace.doc('get_visitor', security='apikey')
    @visitors_namespace.marshal_with(visitor_model)
    @jwt_required()
    @role_required(['admin', 'staff'])
    def get(self, id):
        """
        Obtener información de un visitante por su ID
        """
        # Implementación para obtener un visitante por ID
        visitor = Visitor.query.get_or_404(id)
        return visitor
    
    @visitors_namespace.doc('update_visitor', security='apikey')
    @visitors_namespace.expect(visitor_model)
    @visitors_namespace.marshal_with(visitor_model)
    @jwt_required()
    @role_required(['admin', 'staff'])
    def put(self, id):
        """
        Actualizar datos de un visitante
        """
        visitor = Visitor.query.get_or_404(id)
        data = request.json
        
        # Validar datos del visitante
        errors = validate_visitor_data(data)
        if errors:
            return {'errors': errors}, 400
        
        if 'name' in data:
            visitor.name = data['name']
            
        if 'email' in data:
            visitor.email = data['email']
            
        if 'phone' in data:
            visitor.phone = data['phone']
        
        db.session.commit()
        
        return visitor
    
    @visitors_namespace.doc('delete_visitor', security='apikey')
    @jwt_required()
    @role_required(['admin'])
    def delete(self, id):
        """
        Eliminar un visitante
        """
        visitor = Visitor.query.get_or_404(id)
        
        # Eliminar check-ins asociados
        VisitorCheckIn.query.filter_by(visitor_id=id).delete()
        
        db.session.delete(visitor)
        db.session.commit()
        
        return '', 204

@visitors_namespace.route('/check-in')
class VisitorCheckInResource(Resource):
    """
    Operaciones para registro de visitantes en eventos
    """
    @visitors_namespace.doc('visitor_check_in')
    @visitors_namespace.expect(visitor_check_in_model)
    @validate_required_fields(['visitor_id', 'event_id', 'kiosk_id'])
    def post(self):
        """
        Registrar la asistencia de un visitante a un evento
        """
        # Implementación para registro de visitante en evento
        data = request.json
        
        # Verificar que el evento, visitante y kiosco existan
        event = Event.query.get_or_404(data['event_id'])
        visitor = Visitor.query.get_or_404(data['visitor_id'])
        kiosk = Kiosk.query.get_or_404(data['kiosk_id'])
        
        # Verificar si el evento está activo
        if not event.is_active:
            return {'error': 'El evento no está activo'}, 400
        
        # Verificar si ya existe un check-in para este visitante en este evento
        existing_check_in = VisitorCheckIn.query.filter_by(
            visitor_id=visitor.id,
            event_id=event.id
        ).first()
        
        if existing_check_in:
            return {'message': 'El visitante ya ha sido registrado en este evento'}, 409
        
        # Crear nuevo check-in
        check_in = VisitorCheckIn(
            visitor_id=visitor.id,
            event_id=event.id,
            kiosk_id=kiosk.id
        )
        
        db.session.add(check_in)
        db.session.commit()
        
        return {'message': 'Registro exitoso'}, 201

@visitors_namespace.route('/event/<int:event_id>')
@visitors_namespace.param('event_id', 'Identificador del evento')
class EventVisitors(Resource):
    """
    Operaciones para visitantes de un evento específico
    """
    @visitors_namespace.doc('get_event_visitors', security='apikey')
    @visitors_namespace.marshal_list_with(visitor_model)
    @jwt_required()
    @role_required(['admin', 'staff'])
    def get(self, event_id):
        """
        Obtener lista de visitantes para un evento específico
        """
        # Implementación para obtener visitantes de un evento
        # Primero verificamos que el evento exista
        Event.query.get_or_404(event_id)
        
        # Obtener todos los check-ins para este evento
        check_ins = VisitorCheckIn.query.filter_by(event_id=event_id).all()
        
        # Obtener los visitantes correspondientes
        visitor_ids = [check_in.visitor_id for check_in in check_ins]
        visitors = Visitor.query.filter(Visitor.id.in_(visitor_ids)).all()
        
        return visitors

@visitors_namespace.route('/register')
class VisitorRegistration(Resource):
    """
    Operaciones para registro completo de visitantes (crear visitante y hacer check-in)
    """
    @visitors_namespace.doc('register_visitor')
    @visitors_namespace.expect(visitor_registration_model)
    @validate_required_fields(['name', 'event_id', 'kiosk_id'])
    def post(self):
        """
        Registrar un nuevo visitante y su asistencia a un evento (operación combinada)
        """
        data = request.json
        
        # Validar datos del visitante
        errors = validate_visitor_data(data)
        if errors:
            return {'errors': errors}, 400
        
        # Verificar que el evento y kiosco existan
        event = Event.query.get_or_404(data['event_id'])
        kiosk = Kiosk.query.get_or_404(data['kiosk_id'])
        
        # Verificar si el evento está activo
        if not event.is_active:
            return {'error': 'El evento no está activo'}, 400
        
        # Buscar visitante existente por email
        existing_visitor = None
        if 'email' in data and data['email']:
            existing_visitor = Visitor.query.filter_by(email=data['email']).first()
        
        # Si no existe, crear nuevo visitante
        if not existing_visitor:
            visitor = Visitor(
                name=data['name'],
                email=data.get('email'),
                phone=data.get('phone')
            )
            db.session.add(visitor)
            db.session.flush()  # Obtener el ID sin hacer commit
        else:
            visitor = existing_visitor
            
        # Verificar si ya existe un check-in para este visitante en este evento
        existing_check_in = VisitorCheckIn.query.filter_by(
            visitor_id=visitor.id,
            event_id=event.id
        ).first()
        
        if existing_check_in:
            if not existing_visitor:
                # Rollback si creamos un nuevo visitante
                db.session.rollback()
            return {'message': 'El visitante ya ha sido registrado en este evento'}, 409
        
        # Crear check-in
        check_in = VisitorCheckIn(
            visitor_id=visitor.id,
            event_id=event.id,
            kiosk_id=kiosk.id
        )
        
        db.session.add(check_in)
        db.session.commit()
        
        return {
            'message': 'Registro exitoso',
            'visitor_id': visitor.id,
            'event_id': event.id,
            'check_in_id': check_in.id
        }, 201

@visitors_namespace.route('/stats')
class VisitorStats(Resource):
    """
    Estadísticas de visitantes
    """
    @visitors_namespace.doc('get_visitor_stats', security='apikey')
    @visitors_namespace.marshal_with(visitor_stats_model)
    @jwt_required()
    @role_required(['admin', 'staff'])
    def get(self):
        """
        Obtener estadísticas de visitantes
        """
        # Total de visitantes
        total_visitors = Visitor.query.count()
        
        # Total de check-ins
        total_check_ins = VisitorCheckIn.query.count()
        
        # Visitantes registrados hoy
        today = datetime.utcnow().date()
        today_start = datetime(today.year, today.month, today.day)
        visitors_today = Visitor.query.filter(Visitor.created_at >= today_start).count()
        
        # Check-ins realizados hoy
        check_ins_today = VisitorCheckIn.query.filter(VisitorCheckIn.check_in_time >= today_start).count()
        
        # Evento más popular
        from sqlalchemy import func
        popular_event_query = db.session.query(
            VisitorCheckIn.event_id,
            Event.title,
            func.count(VisitorCheckIn.id).label('count')
        ).join(
            Event, Event.id == VisitorCheckIn.event_id
        ).group_by(
            VisitorCheckIn.event_id, Event.title
        ).order_by(
            func.count(VisitorCheckIn.id).desc()
        ).first()
        
        most_popular_event = None
        if popular_event_query:
            most_popular_event = {
                'id': popular_event_query[0],
                'title': popular_event_query[1],
                'count': popular_event_query[2]
            }
        
        return {
            'total_visitors': total_visitors,
            'total_check_ins': total_check_ins,
            'visitors_today': visitors_today,
            'check_ins_today': check_ins_today,
            'most_popular_event': most_popular_event
        }

@visitors_namespace.route('/export')
class VisitorExport(Resource):
    """
    Operaciones para exportar datos de visitantes
    """
    @visitors_namespace.doc('export_visitors', security='apikey', params={
        'format': 'Formato de exportación (csv o excel, por defecto: csv)',
        'event_id': 'Filtrar por ID de evento',
        'start_date': 'Filtrar desde fecha (YYYY-MM-DD)',
        'end_date': 'Filtrar hasta fecha (YYYY-MM-DD)',
        'has_check_in': 'Filtrar por estado de check-in (true/false)'
    })
    @jwt_required()
    @role_required(['admin', 'staff'])
    def get(self):
        """
        Exportar datos de visitantes en formato CSV o Excel
        """
        # Verificar permisos (solo admin y staff)
        current_user = get_jwt_identity()
        
        # Parámetros de filtrado
        export_format = request.args.get('format', 'csv').lower()
        event_id = request.args.get('event_id', type=int)
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        has_check_in = request.args.get('has_check_in')
        
        if export_format not in ['csv', 'excel']:
            return jsonify({'error': 'Formato no soportado. Use csv o excel'}), 400
        
        # Construir consulta base
        query = Visitor.query
        
        # Aplicar filtros
        if event_id:
            # Subconsulta para visitantes que tienen check-in en el evento
            visitor_ids_with_checkin = db.session.query(VisitorCheckIn.visitor_id).filter_by(event_id=event_id).subquery()
            query = query.filter(Visitor.id.in_(visitor_ids_with_checkin))
        
        # Filtrar por fechas
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                query = query.filter(func.date(Visitor.created_at) >= start_date)
            except ValueError:
                pass  # Ignorar si el formato de fecha es incorrecto
        
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                query = query.filter(func.date(Visitor.created_at) <= end_date)
            except ValueError:
                pass  # Ignorar si el formato de fecha es incorrecto
        
        # Filtrar por estado de check-in (si se especifica)
        if has_check_in is not None:
            has_check_in = has_check_in.lower() == 'true'
            if has_check_in:
                # Visitantes que tienen al menos un check-in
                visitor_ids_with_checkin = db.session.query(VisitorCheckIn.visitor_id).distinct().subquery()
                query = query.filter(Visitor.id.in_(visitor_ids_with_checkin))
            else:
                # Visitantes que no tienen check-in
                visitor_ids_with_checkin = db.session.query(VisitorCheckIn.visitor_id).distinct().subquery()
                query = query.filter(~Visitor.id.in_(visitor_ids_with_checkin))
        
        # Obtener visitantes
        visitors = query.order_by(desc(Visitor.created_at)).all()
        
        # Preparar datos para exportación
        visitor_data = []
        for visitor in visitors:
            visitor_item = {
                'ID': visitor.id,
                'Nombre': visitor.name,
                'Email': visitor.email or '',
                'Teléfono': visitor.phone or '',
                'Fecha de Registro': visitor.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Obtener información de check-ins
            check_ins = VisitorCheckIn.query.filter_by(visitor_id=visitor.id).all()
            check_in_info = []
            for check_in in check_ins:
                event = Event.query.get(check_in.event_id)
                event_name = event.title if event else "Evento desconocido"
                check_in_info.append(f"{event_name} ({check_in.created_at.strftime('%Y-%m-%d %H:%M')})")
            
            visitor_item['Check-ins'] = '; '.join(check_in_info) if check_in_info else 'Ninguno'
            visitor_data.append(visitor_item)
        
        # Exportar según formato solicitado
        if export_format == 'csv':
            # Crear CSV en memoria
            output = io.StringIO()
            fieldnames = ['ID', 'Nombre', 'Email', 'Teléfono', 'Fecha de Registro', 'Check-ins']
            
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            for visitor in visitor_data:
                writer.writerow(visitor)
            
            # Crear respuesta con el archivo
            output.seek(0)
            response = make_response(output.getvalue())
            response.headers['Content-Disposition'] = f'attachment; filename=visitantes_{datetime.now().strftime("%Y%m%d")}.csv'
            response.headers['Content-type'] = 'text/csv'
            return response
        
        else:  # Excel
            # Crear Excel en memoria
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet('Visitantes')
            
            # Añadir información de filtros
            bold = workbook.add_format({'bold': True})
            worksheet.write(0, 0, 'Reporte de Visitantes', bold)
            worksheet.write(1, 0, f'Generado el: {datetime.now().strftime("%Y-%m-%d %H:%M")}')
            
            if event_id:
                event = Event.query.get(event_id)
                if event:
                    worksheet.write(2, 0, f'Evento: {event.title}')
            
            # Cabeceras para datos de visitantes
            headers = ['ID', 'Nombre', 'Email', 'Teléfono', 'Fecha de Registro', 'Check-ins']
            header_format = workbook.add_format({'bold': True, 'bg_color': '#D0D0D0'})
            
            row = 4
            for col, header in enumerate(headers):
                worksheet.write(row, col, header, header_format)
            
            # Datos de visitantes
            row += 1
            for visitor in visitor_data:
                for col, header in enumerate(headers):
                    worksheet.write(row, col, visitor[header])
                row += 1
            
            # Ajustar anchos de columna
            worksheet.set_column(0, 0, 5)  # ID
            worksheet.set_column(1, 1, 25)  # Nombre
            worksheet.set_column(2, 2, 25)  # Email
            worksheet.set_column(3, 3, 15)  # Teléfono
            worksheet.set_column(4, 4, 20)  # Fecha de Registro
            worksheet.set_column(5, 5, 50)  # Check-ins
            
            workbook.close()
            
            # Crear respuesta con el archivo
            output.seek(0)
            response = make_response(output.getvalue())
            response.headers['Content-Disposition'] = f'attachment; filename=visitantes_{datetime.now().strftime("%Y%m%d")}.xlsx'
            response.headers['Content-type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            return response
