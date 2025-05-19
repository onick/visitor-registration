"""
Endpoints mejorados para exportación de datos de eventos con filtros personalizados
"""
from flask import request, jsonify, make_response, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.event import Event
from models.visitor import Visitor, VisitorCheckIn
from models.database import db
from datetime import datetime
from utils.decorators import role_required
import csv
import io
import xlsxwriter
from sqlalchemy import text

export_bp = Blueprint('export', __name__)

@export_bp.route('/api/v1/events/<int:event_id>/export', methods=['GET'])
@jwt_required()
@role_required(['admin', 'staff'])
def export_event_data(event_id):
    """
    Exporta los datos de un evento y sus visitantes con filtros personalizados
    """
    try:
        # Buscar el evento
        event = Event.query.get_or_404(event_id)
        
        # Obtener parámetros de la query
        export_format = request.args.get('format', 'csv').lower()
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        checked_in_filter = request.args.get('checked_in')
        search = request.args.get('search')
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        if export_format not in ['csv', 'excel']:
            return jsonify({'error': 'Formato no soportado. Use csv o excel'}), 400
        
        # Construir query base
        query = Visitor.query.filter_by(event_id=event_id)
        
        # Aplicar filtros
        if start_date:
            try:
                date = datetime.strptime(start_date, '%Y-%m-%d')
                query = query.filter(Visitor.created_at >= date)
            except ValueError:
                return jsonify({'error': 'Formato de fecha incorrecto. Use YYYY-MM-DD'}), 400
        
        if end_date:
            try:
                date = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
                query = query.filter(Visitor.created_at <= date)
            except ValueError:
                return jsonify({'error': 'Formato de fecha incorrecto. Use YYYY-MM-DD'}), 400
        
        if checked_in_filter is not None:
            checked_in_bool = checked_in_filter.lower() == 'true'
            # Subquery para visitantes con check-in
            checked_in_subquery = db.session.query(VisitorCheckIn.visitor_id).filter_by(event_id=event_id).subquery()
            
            if checked_in_bool:
                query = query.filter(Visitor.id.in_(checked_in_subquery))
            else:
                query = query.filter(~Visitor.id.in_(checked_in_subquery))
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    Visitor.name.ilike(search_term),
                    Visitor.email.ilike(search_term),
                    Visitor.registration_code.ilike(search_term)
                )
            )
        
        # Aplicar ordenamiento
        if sort_by in ['name', 'email', 'created_at', 'registration_code']:
            if sort_order == 'asc':
                query = query.order_by(getattr(Visitor, sort_by))
            else:
                query = query.order_by(getattr(Visitor, sort_by).desc())
        
        # Obtener visitantes
        visitors = query.all()
        
        # Preparar datos para exportación
        visitor_data = []
        for visitor in visitors:
            visitor_item = {
                'ID': visitor.id,
                'Código de Registro': visitor.registration_code,
                'Nombre': visitor.name,
                'Email': visitor.email,
                'Teléfono': visitor.phone,
                'Fecha de Registro': visitor.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Verificar check-in
            check_in = VisitorCheckIn.query.filter_by(visitor_id=visitor.id, event_id=event_id).first()
            visitor_item['Check-In'] = 'Sí' if check_in else 'No'
            visitor_item['Fecha Check-In'] = check_in.created_at.strftime('%Y-%m-%d %H:%M:%S') if check_in else ''
            visitor_item['Kiosco'] = f'Kiosco {check_in.kiosk_id}' if check_in else ''
            
            visitor_data.append(visitor_item)
        
        # Calcular estadísticas
        total_visitors = len(visitor_data)
        checked_in_count = sum(1 for v in visitor_data if v['Check-In'] == 'Sí')
        attendance_rate = (checked_in_count / total_visitors * 100) if total_visitors > 0 else 0
        
        # Exportar según formato
        if export_format == 'csv':
            # Crear CSV
            output = io.StringIO()
            fieldnames = ['ID', 'Código de Registro', 'Nombre', 'Email', 'Teléfono', 
                         'Fecha de Registro', 'Check-In', 'Fecha Check-In', 'Kiosco']
            
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            
            # Escribir información del evento
            writer.writerow({})
            writer.writerow({'ID': 'INFORMACIÓN DEL EVENTO'})
            writer.writerow({'ID': 'Evento:', 'Código de Registro': event.title})
            writer.writerow({'ID': 'Fecha:', 'Código de Registro': f"{event.start_date.strftime('%Y-%m-%d')} - {event.end_date.strftime('%Y-%m-%d')}"})
            writer.writerow({'ID': 'Ubicación:', 'Código de Registro': event.location})
            writer.writerow({'ID': 'Total Registrados:', 'Código de Registro': total_visitors})
            writer.writerow({'ID': 'Total Check-ins:', 'Código de Registro': checked_in_count})
            writer.writerow({'ID': 'Tasa de Asistencia:', 'Código de Registro': f'{attendance_rate:.1f}%'})
            writer.writerow({})
            writer.writerow({'ID': 'LISTA DE VISITANTES'})
            
            # Escribir datos de visitantes
            for visitor in visitor_data:
                writer.writerow(visitor)
            
            # Crear respuesta
            output.seek(0)
            response = make_response(output.getvalue())
            filename = f'evento_{event_id}_{event.title.replace(" ", "_")}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            response.headers['Content-Disposition'] = f'attachment; filename={filename}'
            response.headers['Content-type'] = 'text/csv; charset=utf-8'
            return response
            
        else:  # Excel
            # Crear Excel
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output)
            
            # Formatos
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#F99D2A',  # Color CCB
                'font_color': 'white',
                'align': 'center',
                'valign': 'vcenter',
                'border': 1
            })
            
            info_format = workbook.add_format({
                'bold': True,
                'bg_color': '#00BDF2',  # Color CCB secundario
                'font_color': 'white',
                'align': 'left',
                'valign': 'vcenter'
            })
            
            cell_format = workbook.add_format({
                'align': 'left',
                'valign': 'vcenter',
                'border': 1
            })
            
            # Hoja de resumen
            summary_sheet = workbook.add_worksheet('Resumen')
            
            # Información del evento
            summary_sheet.merge_range('A1:D1', 'INFORMACIÓN DEL EVENTO', info_format)
            summary_sheet.write('A2', 'Evento:', header_format)
            summary_sheet.merge_range('B2:D2', event.title, cell_format)
            summary_sheet.write('A3', 'Descripción:', header_format)
            summary_sheet.merge_range('B3:D3', event.description, cell_format)
            summary_sheet.write('A4', 'Fecha:', header_format)
            summary_sheet.merge_range('B4:D4', f"{event.start_date.strftime('%Y-%m-%d')} - {event.end_date.strftime('%Y-%m-%d')}", cell_format)
            summary_sheet.write('A5', 'Ubicación:', header_format)
            summary_sheet.merge_range('B5:D5', event.location, cell_format)
            
            # Estadísticas
            summary_sheet.merge_range('A7:D7', 'ESTADÍSTICAS', info_format)
            summary_sheet.write('A8', 'Total Registrados:', header_format)
            summary_sheet.write('B8', total_visitors, cell_format)
            summary_sheet.write('A9', 'Total Check-ins:', header_format)
            summary_sheet.write('B9', checked_in_count, cell_format)
            summary_sheet.write('A10', 'Tasa de Asistencia:', header_format)
            summary_sheet.write('B10', f'{attendance_rate:.1f}%', cell_format)
            
            # Ajustar anchos
            summary_sheet.set_column('A:A', 20)
            summary_sheet.set_column('B:D', 30)
            
            # Hoja de visitantes
            visitors_sheet = workbook.add_worksheet('Visitantes')
            
            # Encabezados
            headers = ['ID', 'Código de Registro', 'Nombre', 'Email', 'Teléfono', 
                      'Fecha de Registro', 'Check-In', 'Fecha Check-In', 'Kiosco']
            
            for col, header in enumerate(headers):
                visitors_sheet.write(0, col, header, header_format)
            
            # Datos
            row = 1
            for visitor in visitor_data:
                for col, header in enumerate(headers):
                    visitors_sheet.write(row, col, visitor[header], cell_format)
                row += 1
            
            # Ajustar anchos de columna
            column_widths = [5, 15, 25, 30, 15, 20, 10, 20, 10]
            for col, width in enumerate(column_widths):
                visitors_sheet.set_column(col, col, width)
            
            # Crear filtros
            visitors_sheet.autofilter(0, 0, row - 1, len(headers) - 1)
            
            workbook.close()
            
            # Crear respuesta
            output.seek(0)
            response = make_response(output.getvalue())
            filename = f'evento_{event_id}_{event.title.replace(" ", "_")}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            response.headers['Content-Disposition'] = f'attachment; filename={filename}'
            response.headers['Content-type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            return response
            
    except Exception as e:
        return jsonify({'error': f'Error al exportar datos: {str(e)}'}), 500
