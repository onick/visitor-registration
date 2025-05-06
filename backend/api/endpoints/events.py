"""
Endpoints para la gestión de eventos
"""
from flask_restx import Namespace, Resource, fields
from flask import request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.event import Event
from models.visitor import Visitor, VisitorCheckIn
from models.database import db
from datetime import datetime
from utils.validators import validate_required_fields, validate_event_data
from utils.decorators import role_required
import csv
import io
import xlsxwriter

events_namespace = Namespace('events', description='Operaciones relacionadas con eventos')

# Modelos para la documentación de la API
event_model = events_namespace.model('Event', {
    'id': fields.Integer(readonly=True, description='Identificador único del evento'),
    'title': fields.String(required=True, description='Título del evento'),
    'description': fields.String(required=True, description='Descripción del evento'),
    'start_date': fields.DateTime(required=True, description='Fecha de inicio'),
    'end_date': fields.DateTime(required=True, description='Fecha de finalización'),
    'location': fields.String(required=True, description='Ubicación del evento'),
    'image_url': fields.String(description='URL de la imagen del evento'),
    'is_active': fields.Boolean(default=True, description='Estado del evento'),
    'created_at': fields.DateTime(readonly=True, description='Fecha de creación'),
    'updated_at': fields.DateTime(readonly=True, description='Fecha de actualización')
})

@events_namespace.route('/')
class EventList(Resource):
    """
    Operaciones para lista de eventos
    """
    @events_namespace.doc('list_events')
    @events_namespace.marshal_list_with(event_model)
    def get(self):
        """
        Obtener lista de eventos
        """
        # Implementación para obtener todos los eventos desde la base de datos
        events = Event.query.all()
        return events
    
    @events_namespace.doc('create_event', security='apikey')
    @events_namespace.expect(event_model)
    @events_namespace.marshal_with(event_model, code=201)
    @jwt_required()
    @role_required(['admin', 'staff'])
    @validate_required_fields(['title', 'description', 'start_date', 'end_date', 'location'])
    def post(self):
        """
        Crear un nuevo evento
        """
        # Implementación para crear un evento
        data = request.json
        
        # Validar datos del evento
        errors = validate_event_data(data)
        if errors:
            return {'errors': errors}, 400
        
        # Crear nuevo evento
        new_event = Event(
            title=data['title'],
            description=data['description'],
            start_date=datetime.fromisoformat(data['start_date'].replace('Z', '+00:00')),
            end_date=datetime.fromisoformat(data['end_date'].replace('Z', '+00:00')),
            location=data['location'],
            image_url=data.get('image_url'),
            is_active=data.get('is_active', True)
        )
        db.session.add(new_event)
        db.session.commit()
        return new_event, 201

@events_namespace.route('/<int:id>')
@events_namespace.param('id', 'Identificador del evento')
class EventResource(Resource):
    """
    Operaciones para eventos individuales
    """
    @events_namespace.doc('get_event')
    @events_namespace.marshal_with(event_model)
    def get(self, id):
        """
        Obtener un evento por su ID
        """
        # Implementación para obtener un evento por ID
        event = Event.query.get_or_404(id)
        return event
    
    @events_namespace.doc('update_event', security='apikey')
    @events_namespace.expect(event_model)
    @events_namespace.marshal_with(event_model)
    @jwt_required()
    @role_required(['admin', 'staff'])
    def put(self, id):
        """
        Actualizar un evento
        """
        # Implementación para actualizar un evento
        event = Event.query.get_or_404(id)
        data = request.json
        
        # Validar datos del evento si se proporcionan campos críticos
        if any(field in data for field in ['title', 'description', 'start_date', 'end_date', 'location']):
            errors = validate_event_data(data)
            if errors:
                return {'errors': errors}, 400
        
        # Actualizar campos
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
        return event
    
    @events_namespace.doc('delete_event', security='apikey')
    @jwt_required()
    @role_required(['admin'])
    def delete(self, id):
        """
        Eliminar un evento
        """
        # Implementación para eliminar un evento
        event = Event.query.get_or_404(id)
        db.session.delete(event)
        db.session.commit()
        return '', 204

# Ruta adicional para obtener eventos activos
@events_namespace.route('/active')
class ActiveEventList(Resource):
    """
    Operaciones para eventos activos
    """
    @events_namespace.doc('list_active_events')
    @events_namespace.marshal_list_with(event_model)
    def get(self):
        """
        Obtener lista de eventos activos
        """
        active_events = Event.query.filter_by(is_active=True).all()
        return active_events

# Ruta para búsqueda de eventos
@events_namespace.route('/search')
class EventSearch(Resource):
    """
    Operaciones para búsqueda de eventos
    """
    @events_namespace.doc('search_events')
    @events_namespace.marshal_list_with(event_model)
    def get(self):
        """
        Buscar eventos por título, descripción o ubicación
        """
        search_term = request.args.get('q', '')
        
        if not search_term:
            return [], 200
        
        # Búsqueda por título, descripción o ubicación
        search_term = f"%{search_term}%"
        events = Event.query.filter(
            db.or_(
                Event.title.ilike(search_term),
                Event.description.ilike(search_term),
                Event.location.ilike(search_term)
            )
        ).all()
        
        return events, 200

@events_namespace.route('/<int:event_id>/export')
@events_namespace.param('event_id', 'Identificador del evento')
class EventExport(Resource):
    """
    Operaciones para exportar datos de un evento
    """
    @events_namespace.doc('export_event_data', security='apikey', params={
        'format': 'Formato de exportación (csv o excel, por defecto: csv)'
    })
    @jwt_required()
    @role_required(['admin', 'staff'])
    def get(self, event_id):
        """
        Exporta los datos de un evento y sus visitantes en formato CSV o Excel
        """
        # Verificar permisos (solo admin y staff)
        current_user = get_jwt_identity()
        
        # Buscar el evento
        event = Event.query.get_or_404(event_id)
        
        # Obtener formato (csv por defecto)
        export_format = request.args.get('format', 'csv').lower()
        if export_format not in ['csv', 'excel']:
            return jsonify({'error': 'Formato no soportado. Use csv o excel'}), 400
        
        # Obtener visitantes del evento
        visitors = Visitor.query.filter_by(event_id=event_id).all()
        
        # Preparar datos para exportación
        visitor_data = []
        for visitor in visitors:
            visitor_item = {
                'ID': visitor.id,
                'Nombre': visitor.name,
                'Email': visitor.email,
                'Teléfono': visitor.phone,
                'Fecha de Registro': visitor.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Verificar si el visitante tiene check-in
            check_in = VisitorCheckIn.query.filter_by(visitor_id=visitor.id, event_id=event_id).first()
            visitor_item['Check-In'] = 'Sí' if check_in else 'No'
            visitor_item['Fecha Check-In'] = check_in.created_at.strftime('%Y-%m-%d %H:%M:%S') if check_in else 'N/A'
            visitor_item['Kiosco Check-In'] = check_in.kiosk_id if check_in else 'N/A'
            
            visitor_data.append(visitor_item)
        
        # Exportar según formato solicitado
        if export_format == 'csv':
            # Crear CSV en memoria
            output = io.StringIO()
            fieldnames = ['ID', 'Nombre', 'Email', 'Teléfono', 'Fecha de Registro', 'Check-In', 'Fecha Check-In', 'Kiosco Check-In']
            
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            for visitor in visitor_data:
                writer.writerow(visitor)
            
            # Crear respuesta con el archivo
            output.seek(0)
            response = make_response(output.getvalue())
            response.headers['Content-Disposition'] = f'attachment; filename=evento_{event_id}_{datetime.now().strftime("%Y%m%d")}.csv'
            response.headers['Content-type'] = 'text/csv'
            return response
        
        else:  # Excel
            # Crear Excel en memoria
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet('Visitantes')
            
            # Añadir información del evento
            bold = workbook.add_format({'bold': True})
            worksheet.write(0, 0, 'Evento:', bold)
            worksheet.write(0, 1, event.title)
            worksheet.write(1, 0, 'Descripción:', bold)
            worksheet.write(1, 1, event.description)
            worksheet.write(2, 0, 'Fecha:', bold)
            worksheet.write(2, 1, f"{event.start_date.strftime('%Y-%m-%d')} - {event.end_date.strftime('%Y-%m-%d')}")
            worksheet.write(3, 0, 'Ubicación:', bold)
            worksheet.write(3, 1, event.location)
            
            # Cabeceras para datos de visitantes
            headers = ['ID', 'Nombre', 'Email', 'Teléfono', 'Fecha de Registro', 'Check-In', 'Fecha Check-In', 'Kiosco Check-In']
            header_format = workbook.add_format({'bold': True, 'bg_color': '#D0D0D0'})
            
            row = 5
            for col, header in enumerate(headers):
                worksheet.write(row, col, header, header_format)
            
            # Datos de visitantes
            row += 1
            for visitor in visitor_data:
                for col, header in enumerate(headers):
                    worksheet.write(row, col, visitor[header])
                row += 1
            
            # Ajustar anchos de columna
            for col, header in enumerate(headers):
                worksheet.set_column(col, col, len(header) + 2)
            
            workbook.close()
            
            # Crear respuesta con el archivo
            output.seek(0)
            response = make_response(output.getvalue())
            response.headers['Content-Disposition'] = f'attachment; filename=evento_{event_id}_{datetime.now().strftime("%Y%m%d")}.xlsx'
            response.headers['Content-type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            return response
