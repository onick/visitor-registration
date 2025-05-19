"""
Servicio para el envío de correos electrónicos
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def get_smtp_config():
    """Obtener configuración de SMTP desde variables de entorno"""
    return {
        'server': os.environ.get('SMTP_SERVER', 'smtp.gmail.com'),
        'port': int(os.environ.get('SMTP_PORT', 587)),
        'username': os.environ.get('SMTP_USERNAME', ''),
        'password': os.environ.get('SMTP_PASSWORD', ''),
        'from_email': os.environ.get('EMAIL_FROM', 'noreply@ccb.do'),
        'from_name': os.environ.get('EMAIL_FROM_NAME', 'Centro Cultural Banreservas')
    }

def send_email(to_email, subject, html_content, text_content=None):
    """
    Enviar un correo electrónico
    
    Args:
        to_email (str): Dirección de correo del destinatario
        subject (str): Asunto del correo
        html_content (str): Contenido HTML del correo
        text_content (str, optional): Contenido texto plano
    
    Returns:
        bool: True si se envió correctamente, False si hubo un error
    """
    # Simular envío para desarrollo
    if os.environ.get('FLASK_ENV') == 'development':
        print(f"\n===== CORREO SIMULADO =====")
        print(f"Para: {to_email}")
        print(f"Asunto: {subject}")
        print(f"Contenido HTML: {html_content}")
        if text_content:
            print(f"Contenido Texto: {text_content}")
        print("=============================\n")
        return True
    
    # Obtener configuración
    config = get_smtp_config()
    
    # Si no hay configuración de SMTP, simular el envío
    if not config['username'] or not config['password']:
        print(f"Simulando envío de correo a {to_email}: {subject}")
        return True
    
    # Crear mensaje
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = f"{config['from_name']} <{config['from_email']}>"
    msg['To'] = to_email
    
    # Añadir contenido
    if text_content:
        msg.attach(MIMEText(text_content, 'plain'))
    
    msg.attach(MIMEText(html_content, 'html'))
    
    # Enviar correo
    try:
        with smtplib.SMTP(config['server'], config['port']) as server:
            server.starttls()
            server.login(config['username'], config['password'])
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Error al enviar correo: {str(e)}")
        return False

def send_invitation_email(to_email, name, event_type, event_name, registration_code):
    """
    Enviar correo de invitación a un evento
    
    Args:
        to_email (str): Correo del visitante
        name (str): Nombre del visitante
        event_type (str): Tipo de evento (cine, exposición, etc.)
        event_name (str): Nombre del evento
        registration_code (str): Código de registro del visitante
    
    Returns:
        bool: True si se envió correctamente
    """
    subject = f"Invitación a {event_name} - Centro Cultural Banreservas"
    
    # Contenido en HTML
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="https://ccb.org.do/images/logo-ccb.png" alt="Centro Cultural Banreservas" style="max-width: 200px;">
        </div>
        
        <h2 style="color: #F99D2A; margin-bottom: 20px;">Hola {name},</h2>
        
        <p style="font-size: 16px; line-height: 1.5; color: #333;">
            Hemos notado tu interés en eventos de <strong>{event_type}</strong> y queremos invitarte a:
        </p>
        
        <div style="background-color: #f9f9f9; padding: 15px; border-radius: 4px; margin: 20px 0;">
            <h3 style="color: #00BDF2; margin-top: 0;">{event_name}</h3>
        </div>
        
        <p style="font-size: 16px; line-height: 1.5; color: #333;">
            Para hacer check-in el día del evento, simplemente presenta tu código de registro:
        </p>
        
        <div style="text-align: center; margin: 25px 0;">
            <div style="background-color: #F99D2A; color: white; font-size: 28px; font-weight: bold; padding: 10px 20px; border-radius: 4px; display: inline-block;">
                {registration_code}
            </div>
        </div>
        
        <p style="font-size: 16px; line-height: 1.5; color: #333;">
            ¡Esperamos verte pronto en nuestro centro cultural!
        </p>
        
        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #777; text-align: center;">
            &copy; Centro Cultural Banreservas 2025<br>
            <em>Este es un correo automático. Por favor no responda a este mensaje.</em>
        </div>
    </div>
    """
    
    # Versión texto plano
    text_content = f"""
    Hola {name},
    
    Hemos notado tu interés en eventos de {event_type} y queremos invitarte a:
    
    {event_name}
    
    Para hacer check-in el día del evento, simplemente presenta tu código de registro: {registration_code}
    
    ¡Esperamos verte pronto en nuestro centro cultural!
    
    Centro Cultural Banreservas 2025
    Este es un correo automático. Por favor no responda a este mensaje.
    """
    
    return send_email(to_email, subject, html_content, text_content)
