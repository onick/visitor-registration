"""
Tareas asíncronas usando Celery
"""
from celery import Celery
from flask import Flask
import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

celery = Celery(__name__)

def init_celery(app: Flask):
    """
    Inicializa Celery con la configuración de la aplicación Flask
    
    Args:
        app (Flask): Aplicación Flask
    """
    celery.conf.update(app.config)
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery

@celery.task(name="tasks.send_email")
def send_email(to, subject, body, is_html=False):
    """
    Envía un correo electrónico
    
    Args:
        to (str): Destinatario
        subject (str): Asunto
        body (str): Cuerpo del mensaje
        is_html (bool): Indica si el cuerpo es HTML
        
    Returns:
        bool: True si se envió correctamente, False en caso contrario
    """
    from flask import current_app
    
    # Obtener configuración de correo
    mail_server = current_app.config.get('MAIL_SERVER')
    mail_port = current_app.config.get('MAIL_PORT')
    mail_username = current_app.config.get('MAIL_USERNAME')
    mail_password = current_app.config.get('MAIL_PASSWORD')
    mail_use_tls = current_app.config.get('MAIL_USE_TLS')
    mail_use_ssl = current_app.config.get('MAIL_USE_SSL')
    mail_default_sender = current_app.config.get('MAIL_DEFAULT_SENDER')
    
    if not mail_server:
        current_app.logger.error("No se ha configurado el servidor de correo")
        return False
    
    try:
        # Crear mensaje
        msg = MIMEMultipart()
        msg['From'] = mail_default_sender
        msg['To'] = to
        msg['Subject'] = subject
        
        # Agregar cuerpo
        if is_html:
            msg.attach(MIMEText(body, 'html'))
        else:
            msg.attach(MIMEText(body, 'plain'))
        
        # Conectar al servidor
        if mail_use_ssl:
            server = smtplib.SMTP_SSL(mail_server, mail_port)
        else:
            server = smtplib.SMTP(mail_server, mail_port)
            if mail_use_tls:
                server.starttls()
        
        # Iniciar sesión si es necesario
        if mail_username and mail_password:
            server.login(mail_username, mail_password)
        
        # Enviar correo
        server.send_message(msg)
        server.quit()
        
        current_app.logger.info(f"Correo enviado a {to}: {subject}")
        return True
    except Exception as e:
        current_app.logger.error(f"Error al enviar correo: {str(e)}")
        return False

@celery.task(name="tasks.send_registration_confirmation")
def send_registration_confirmation(visitor_data, event_data):
    """
    Envía un correo de confirmación de registro a un evento
    
    Args:
        visitor_data (dict): Datos del visitante
        event_data (dict): Datos del evento
        
    Returns:
        bool: True si se envió correctamente, False en caso contrario
    """
    to = visitor_data.get('email')
    if not to:
        return False
    
    subject = f"Confirmación de Registro - {event_data.get('title')}"
    
    # Crear cuerpo del mensaje
    body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #00AEEF; color: white; padding: 10px 20px; text-align: center; }}
            .content {{ padding: 20px; }}
            .footer {{ font-size: 12px; text-align: center; margin-top: 30px; color: #777; }}
            .code {{ font-size: 24px; font-weight: bold; text-align: center; margin: 20px 0; padding: 10px; background-color: #f0f0f0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Confirmación de Registro</h1>
            </div>
            <div class="content">
                <p>Hola, {visitor_data.get('name')}:</p>
                <p>Tu registro para el evento <strong>{event_data.get('title')}</strong> ha sido confirmado.</p>
                <p>Detalles del evento:</p>
                <ul>
                    <li><strong>Fecha:</strong> {event_data.get('start_date')}</li>
                    <li><strong>Lugar:</strong> {event_data.get('location')}</li>
                </ul>
                <p>Tu código de registro es:</p>
                <div class="code">{visitor_data.get('registration_code')}</div>
                <p>Presenta este código en la entrada del evento para completar tu check-in.</p>
                <p>¡Gracias por registrarte!</p>
            </div>
            <div class="footer">
                <p>Este es un mensaje automático, por favor no respondas a este correo.</p>
                <p>© Centro Cultural Banreservas</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email.delay(to, subject, body, is_html=True)

@celery.task(name="tasks.send_event_reminder")
def send_event_reminder(visitor_data, event_data):
    """
    Envía un recordatorio de evento a un visitante
    
    Args:
        visitor_data (dict): Datos del visitante
        event_data (dict): Datos del evento
        
    Returns:
        bool: True si se envió correctamente, False en caso contrario
    """
    to = visitor_data.get('email')
    if not to:
        return False
    
    subject = f"Recordatorio - {event_data.get('title')}"
    
    # Crear cuerpo del mensaje
    body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #FF9800; color: white; padding: 10px 20px; text-align: center; }}
            .content {{ padding: 20px; }}
            .footer {{ font-size: 12px; text-align: center; margin-top: 30px; color: #777; }}
            .code {{ font-size: 24px; font-weight: bold; text-align: center; margin: 20px 0; padding: 10px; background-color: #f0f0f0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Recordatorio de Evento</h1>
            </div>
            <div class="content">
                <p>Hola, {visitor_data.get('name')}:</p>
                <p>Te recordamos que el evento <strong>{event_data.get('title')}</strong> está próximo a comenzar.</p>
                <p>Detalles del evento:</p>
                <ul>
                    <li><strong>Fecha:</strong> {event_data.get('start_date')}</li>
                    <li><strong>Lugar:</strong> {event_data.get('location')}</li>
                </ul>
                <p>Tu código de registro es:</p>
                <div class="code">{visitor_data.get('registration_code')}</div>
                <p>Presenta este código en la entrada del evento para completar tu check-in.</p>
                <p>¡Te esperamos!</p>
            </div>
            <div class="footer">
                <p>Este es un mensaje automático, por favor no respondas a este correo.</p>
                <p>© Centro Cultural Banreservas</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email.delay(to, subject, body, is_html=True)

@celery.task(name="tasks.schedule_event_reminders")
def schedule_event_reminders():
    """
    Programa recordatorios para eventos próximos
    """
    from models.event import Event
    from models.visitor import EventVisitor
    from models.database import db
    from flask import current_app
    
    try:
        # Buscar eventos que comienzan en las próximas 24 horas
        now = datetime.utcnow()
        tomorrow = now + timedelta(days=1)
        
        upcoming_events = Event.query.filter(
            Event.start_date.between(now, tomorrow),
            Event.is_active == True
        ).all()
        
        for event in upcoming_events:
            # Buscar visitantes registrados para este evento
            registrations = EventVisitor.query.filter(
                EventVisitor.event_id == event.id,
                EventVisitor.status == 'REGISTERED'
            ).all()
            
            event_dict = event.to_dict()
            
            # Enviar recordatorio a cada visitante
            for registration in registrations:
                visitor_dict = registration.visitor.to_dict() if registration.visitor else {}
                visitor_dict['registration_code'] = registration.registration_code
                
                send_event_reminder.delay(visitor_dict, event_dict)
                
                current_app.logger.info(f"Recordatorio programado para visitante {visitor_dict.get('name')} - Evento: {event_dict.get('title')}")
        
        return True
    except Exception as e:
        current_app.logger.error(f"Error al programar recordatorios: {str(e)}")
        return False

@celery.task(name="tasks.generate_event_report")
def generate_event_report(event_id, format='json'):
    """
    Genera un reporte de un evento
    
    Args:
        event_id (int): ID del evento
        format (str): Formato del reporte (json, csv, etc.)
        
    Returns:
        str: Ruta del archivo generado
    """
    from models.event import Event
    from models.visitor import EventVisitor
    from flask import current_app
    import csv
    
    try:
        event = Event.query.get(event_id)
        if not event:
            current_app.logger.error(f"No se encontró el evento con ID {event_id}")
            return None
        
        # Obtener registros para este evento
        registrations = EventVisitor.query.filter_by(event_id=event_id).all()
        
        # Preparar datos para el reporte
        report_data = {
            'event': event.to_dict(),
            'statistics': {
                'total_registrations': len([r for r in registrations if r.status != 'CANCELED']),
                'checked_in': len([r for r in registrations if r.status == 'CHECKED_IN']),
                'no_show': len([r for r in registrations if r.status == 'NO_SHOW']),
                'canceled': len([r for r in registrations if r.status == 'CANCELED']),
                'attendance_rate': round(len([r for r in registrations if r.status == 'CHECKED_IN']) / 
                                       max(1, len([r for r in registrations if r.status != 'CANCELED'])) * 100, 2)
            },
            'registrations': [
                {
                    'id': r.id,
                    'visitor_name': r.visitor.name if r.visitor else 'N/A',
                    'visitor_email': r.visitor.email if r.visitor else 'N/A',
                    'registration_code': r.registration_code,
                    'registration_date': r.registration_date.isoformat(),
                    'check_in_time': r.check_in_time.isoformat() if r.check_in_time else None,
                    'status': r.status
                }
                for r in registrations
            ]
        }
        
        # Generar archivo según formato
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"event_report_{event_id}_{timestamp}"
        
        if format == 'json':
            output_path = os.path.join(current_app.config.get('UPLOADS_FOLDER'), f"{filename}.json")
            with open(output_path, 'w') as f:
                json.dump(report_data, f, indent=2)
            return output_path
        
        elif format == 'csv':
            output_path = os.path.join(current_app.config.get('UPLOADS_FOLDER'), f"{filename}.csv")
            with open(output_path, 'w', newline='') as f:
                writer = csv.writer(f)
                
                # Escribir encabezados
                writer.writerow(['ID', 'Visitante', 'Email', 'Código', 'Fecha de Registro', 'Check-in', 'Estado'])
                
                # Escribir datos
                for reg in report_data['registrations']:
                    writer.writerow([
                        reg['id'],
                        reg['visitor_name'],
                        reg['visitor_email'],
                        reg['registration_code'],
                        reg['registration_date'],
                        reg['check_in_time'] or 'N/A',
                        reg['status']
                    ])
            return output_path
        
        else:
            current_app.logger.error(f"Formato no soportado: {format}")
            return None
            
    except Exception as e:
        current_app.logger.error(f"Error al generar reporte: {str(e)}")
        return None 