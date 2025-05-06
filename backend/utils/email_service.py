"""
Servicio para envío de correos electrónicos
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from datetime import datetime

# Configuración desde variables de entorno
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_USERNAME = os.environ.get('SMTP_USERNAME', '')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
EMAIL_FROM = os.environ.get('EMAIL_FROM', 'noreply@centroculturalbanreservas.com')
EMAIL_ENABLED = os.environ.get('EMAIL_ENABLED', 'false').lower() == 'true'

# Configurar logger
logger = logging.getLogger(__name__)

def send_email(to, subject, html_content, text_content=None):
    """
    Envía un correo electrónico a un destinatario
    
    Args:
        to (str): Dirección de correo del destinatario
        subject (str): Asunto del correo
        html_content (str): Contenido HTML del mensaje
        text_content (str, opcional): Contenido de texto plano del mensaje (alternativa)
        
    Returns:
        bool: True si el correo fue enviado correctamente, False en caso contrario
    """
    # Si el servicio de correo está deshabilitado, solo registrar y salir
    if not EMAIL_ENABLED:
        logger.info(f"Email enviado simulado: To={to}, Subject={subject}")
        return True
    
    # Si falta la configuración de SMTP, registrar error y salir
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        logger.error("Configuración de SMTP incompleta. Verifique las variables de entorno.")
        return False
    
    # Crear mensaje
    message = MIMEMultipart('alternative')
    message['Subject'] = subject
    message['From'] = EMAIL_FROM
    message['To'] = to
    
    # Contenido de texto plano (alternativa para clientes que no soportan HTML)
    if text_content:
        part1 = MIMEText(text_content, 'plain')
        message.attach(part1)
    
    # Contenido HTML
    part2 = MIMEText(html_content, 'html')
    message.attach(part2)
    
    # Enviar correo
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Iniciar TLS
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(EMAIL_FROM, to, message.as_string())
        server.quit()
        logger.info(f"Email enviado correctamente: To={to}, Subject={subject}")
        return True
    except Exception as e:
        logger.error(f"Error al enviar email: {str(e)}")
        return False

def send_welcome_email(user_name, user_email):
    """
    Envía un correo de bienvenida a un nuevo usuario
    
    Args:
        user_name (str): Nombre del usuario
        user_email (str): Correo del usuario
        
    Returns:
        bool: True si el correo fue enviado correctamente, False en caso contrario
    """
    subject = "Bienvenido al Sistema de Registro de Visitantes"
    
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
            .container {{ width: 100%; max-width: 600px; margin: 0 auto; }}
            .header {{ background-color: #003b71; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; }}
            .footer {{ background-color: #f5f5f5; padding: 10px; text-align: center; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>¡Bienvenido al Centro Cultural Banreservas!</h1>
            </div>
            <div class="content">
                <p>Hola {user_name},</p>
                <p>Tu cuenta ha sido creada exitosamente en nuestro Sistema de Registro de Visitantes.</p>
                <p>A partir de ahora, podrás gestionar los visitantes, eventos y kioscos del Centro Cultural Banreservas.</p>
                <p>Si tienes alguna pregunta, no dudes en contactar al administrador del sistema.</p>
                <p>¡Gracias por ser parte de nuestro equipo!</p>
            </div>
            <div class="footer">
                <p>Centro Cultural Banreservas &copy; {datetime.now().year}. Todos los derechos reservados.</p>
                <p>Este es un correo generado automáticamente, por favor no responda a este mensaje.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    ¡Bienvenido al Centro Cultural Banreservas!
    
    Hola {user_name},
    
    Tu cuenta ha sido creada exitosamente en nuestro Sistema de Registro de Visitantes.
    
    A partir de ahora, podrás gestionar los visitantes, eventos y kioscos del Centro Cultural Banreservas.
    
    Si tienes alguna pregunta, no dudes en contactar al administrador del sistema.
    
    ¡Gracias por ser parte de nuestro equipo!
    
    Centro Cultural Banreservas. Todos los derechos reservados.
    Este es un correo generado automáticamente, por favor no responda a este mensaje.
    """
    
    return send_email(user_email, subject, html_content, text_content) 