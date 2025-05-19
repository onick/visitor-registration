"""
API endpoint para datos analíticos del dashboard
"""
from flask import jsonify
from datetime import datetime, timedelta
from sqlalchemy import func, extract, distinct
from models.visitor import Visitor, VisitorCheckIn
from models.event import Event
from models.database import db

def init_dashboard_analytics(app):
    
    @app.route('/api/dashboard-data', methods=['GET'])
    def get_dashboard_analytics():
        """
        Obtener datos analíticos para los gráficos del dashboard
        """
        try:
            # 1. Tendencia de asistencia por día (últimos 30 días)
            attendance_trend = get_attendance_trend()
            
            # 2. Comparativa por tipos de eventos
            event_types_comparison = get_event_types_comparison()
            
            # 3. Mapa de calor de días y horas de mayor tráfico
            traffic_heatmap = get_traffic_heatmap()
            
            # 4. Distribución por edad o región (usando datos simulados por ahora)
            visitor_distribution = get_visitor_distribution()
            
            # 5. Comparación de asistencia entre salas
            room_comparison = get_room_comparison()
            
            # 6. Estadísticas adicionales
            peak_hours = get_peak_hours()
            monthly_growth = get_monthly_growth()
            
            return jsonify({
                'success': True,
                'data': {
                    'attendanceTrend': attendance_trend,
                    'eventTypesComparison': event_types_comparison,
                    'trafficHeatmap': traffic_heatmap,
                    'visitorDistribution': visitor_distribution,
                    'roomComparison': room_comparison,
                    'peakHours': peak_hours,
                    'monthlyGrowth': monthly_growth
                }
            })
            
        except Exception as e:
            print(f"Error obteniendo datos del dashboard: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    def get_attendance_trend():
        """Obtener tendencia de asistencia en los últimos 30 días"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=29)
        
        # Crear un diccionario con todos los días inicializados en 0
        date_dict = {}
        current_date = start_date
        while current_date <= end_date:
            date_dict[current_date.strftime('%Y-%m-%d')] = 0
            current_date += timedelta(days=1)
        
        # Consultar asistencia real
        attendance_data = db.session.query(
            func.date(VisitorCheckIn.check_in_time).label('date'),
            func.count(VisitorCheckIn.id).label('count')
        ).filter(
            VisitorCheckIn.check_in_time >= start_date
        ).group_by(
            func.date(VisitorCheckIn.check_in_time)
        ).all()
        
        # Actualizar el diccionario con datos reales
        for record in attendance_data:
            date_str = record.date.strftime('%Y-%m-%d')
            if date_str in date_dict:
                date_dict[date_str] = record.count
        
        # Convertir a lista ordenada
        result = []
        for date_str in sorted(date_dict.keys()):
            result.append({
                'date': date_str,
                'visitors': date_dict[date_str]
            })
        
        return result
    
    def get_event_types_comparison():
        """Comparativa entre tipos de eventos"""
        # Definir tipos de eventos basados en palabras clave en los títulos
        event_types = {
            'Charlas': ['charla', 'conferencia', 'seminario', 'ponencia'],
            'Exposiciones': ['exposición', 'exposicion', 'exhibición', 'muestra'],
            'Teatro': ['teatro', 'obra', 'drama', 'comedia'],
            'Música': ['concierto', 'música', 'musica', 'recital'],
            'Talleres': ['taller', 'workshop', 'curso'],
            'Otros': []
        }
        
        # Obtener todos los eventos con sus visitantes
        events = db.session.query(
            Event.id,
            Event.title,
            func.count(VisitorCheckIn.id).label('visitor_count')
        ).outerjoin(
            VisitorCheckIn, Event.id == VisitorCheckIn.event_id
        ).group_by(
            Event.id, Event.title
        ).all()
        
        # Clasificar eventos por tipo
        type_counts = {type_name: 0 for type_name in event_types.keys()}
        event_count_by_type = {type_name: 0 for type_name in event_types.keys()}
        
        for event in events:
            title_lower = event.title.lower()
            event_classified = False
            
            for type_name, keywords in event_types.items():
                if type_name == 'Otros':
                    continue
                    
                for keyword in keywords:
                    if keyword in title_lower:
                        type_counts[type_name] += event.visitor_count
                        event_count_by_type[type_name] += 1
                        event_classified = True
                        break
                
                if event_classified:
                    break
            
            if not event_classified:
                type_counts['Otros'] += event.visitor_count
                event_count_by_type['Otros'] += 1
        
        # Formatear resultado
        result = []
        for type_name, count in type_counts.items():
            events_count = event_count_by_type[type_name]
            avg_attendance = count / events_count if events_count > 0 else 0
            
            result.append({
                'type': type_name,
                'totalVisitors': count,
                'eventsCount': events_count,
                'avgAttendance': round(avg_attendance, 1)
            })
        
        return result
    
    def get_traffic_heatmap():
        """Mapa de calor de días y horas de mayor tráfico"""
        # Obtener check-ins de los últimos 3 meses
        start_date = datetime.now() - timedelta(days=90)
        
        check_ins = db.session.query(
            extract('dow', VisitorCheckIn.check_in_time).label('day_of_week'),
            extract('hour', VisitorCheckIn.check_in_time).label('hour'),
            func.count(VisitorCheckIn.id).label('count')
        ).filter(
            VisitorCheckIn.check_in_time >= start_date
        ).group_by(
            extract('dow', VisitorCheckIn.check_in_time),
            extract('hour', VisitorCheckIn.check_in_time)
        ).all()
        
        # Crear matriz para el mapa de calor
        heatmap_data = []
        for check_in in check_ins:
            heatmap_data.append({
                'day': int(check_in.day_of_week),
                'hour': int(check_in.hour),
                'value': check_in.count
            })
        
        return heatmap_data
    
    def get_visitor_distribution():
        """Distribución de visitantes (simulada por edad)"""
        # Como no tenemos datos de edad, simularemos una distribución típica
        age_ranges = [
            {'range': '18-25', 'percentage': 15},
            {'range': '26-35', 'percentage': 28},
            {'range': '36-45', 'percentage': 25},
            {'range': '46-55', 'percentage': 18},
            {'range': '56-65', 'percentage': 10},
            {'range': '65+', 'percentage': 4}
        ]
        
        total_visitors = db.session.query(func.count(Visitor.id)).scalar()
        
        result = []
        for age_range in age_ranges:
            count = int(total_visitors * age_range['percentage'] / 100)
            result.append({
                'range': age_range['range'],
                'count': count,
                'percentage': age_range['percentage']
            })
        
        return result
    
    def get_room_comparison():
        """Comparación de asistencia entre salas"""
        # Obtener eventos agrupados por ubicación
        room_data = db.session.query(
            Event.location,
            func.count(distinct(Event.id)).label('event_count'),
            func.count(VisitorCheckIn.id).label('visitor_count')
        ).outerjoin(
            VisitorCheckIn, Event.id == VisitorCheckIn.event_id
        ).group_by(
            Event.location
        ).all()
        
        # Calcular métricas adicionales
        result = []
        for room in room_data:
            avg_attendance = room.visitor_count / room.event_count if room.event_count > 0 else 0
            
            result.append({
                'room': room.location,
                'eventCount': room.event_count,
                'totalVisitors': room.visitor_count,
                'avgAttendance': round(avg_attendance, 1)
            })
        
        # Ordenar por total de visitantes
        result.sort(key=lambda x: x['totalVisitors'], reverse=True)
        
        return result[:5]  # Top 5 salas
    
    def get_peak_hours():
        """Obtener horas pico de asistencia"""
        peak_data = db.session.query(
            extract('hour', VisitorCheckIn.check_in_time).label('hour'),
            func.count(VisitorCheckIn.id).label('count')
        ).group_by(
            extract('hour', VisitorCheckIn.check_in_time)
        ).order_by(
            func.count(VisitorCheckIn.id).desc()
        ).limit(5).all()
        
        result = []
        for record in peak_data:
            hour = int(record.hour)
            hour_str = f"{hour:02d}:00"
            result.append({
                'hour': hour_str,
                'count': record.count
            })
        
        return result
    
    def get_monthly_growth():
        """Obtener crecimiento mensual de visitantes"""
        # Últimos 6 meses
        end_date = datetime.now()
        start_date = end_date - timedelta(days=180)
        
        monthly_data = db.session.query(
            extract('year', VisitorCheckIn.check_in_time).label('year'),
            extract('month', VisitorCheckIn.check_in_time).label('month'),
            func.count(VisitorCheckIn.id).label('count')
        ).filter(
            VisitorCheckIn.check_in_time >= start_date
        ).group_by(
            extract('year', VisitorCheckIn.check_in_time),
            extract('month', VisitorCheckIn.check_in_time)
        ).order_by(
            extract('year', VisitorCheckIn.check_in_time),
            extract('month', VisitorCheckIn.check_in_time)
        ).all()
        
        result = []
        prev_count = 0
        
        for record in monthly_data:
            month_name = datetime(int(record.year), int(record.month), 1).strftime('%B %Y')
            growth_rate = 0
            
            if prev_count > 0:
                growth_rate = ((record.count - prev_count) / prev_count) * 100
            
            result.append({
                'month': month_name,
                'visitors': record.count,
                'growthRate': round(growth_rate, 1)
            })
            
            prev_count = record.count
        
        return result
