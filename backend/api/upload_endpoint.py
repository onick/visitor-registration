"""
Endpoint para carga de imágenes de eventos
"""
from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required
from models.event import Event
from models.database import db
from utils.decorators import role_required
import os
import uuid
from werkzeug.utils import secure_filename
from datetime import datetime

upload_bp = Blueprint('upload', __name__)

# Configuración de uploads
UPLOAD_FOLDER = 'uploads/events'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

def allowed_file(filename):
    """Verificar si el archivo es de un tipo permitido"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/api/v1/events/<int:event_id>/upload-image', methods=['POST'])
@jwt_required()
@role_required(['admin', 'staff'])
def upload_event_image(event_id):
    """Subir imagen de portada para un evento"""
    try:
        # Verificar que el evento existe
        event = Event.query.get_or_404(event_id)
        
        # Verificar que se envió un archivo
        if 'image' not in request.files:
            return jsonify({'error': 'No se envió ningún archivo'}), 400
        
        file = request.files['image']
        
        # Verificar que el archivo tiene nombre
        if file.filename == '':
            return jsonify({'error': 'El archivo no tiene nombre'}), 400
        
        # Verificar el tipo de archivo
        if not allowed_file(file.filename):
            return jsonify({
                'error': 'Tipo de archivo no permitido. Solo se aceptan: ' + 
                ', '.join(ALLOWED_EXTENSIONS)
            }), 400
        
        # Verificar el tamaño del archivo
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({
                'error': f'El archivo es demasiado grande. Máximo: {MAX_FILE_SIZE/1024/1024}MB'
            }), 400
        
        # Crear directorio si no existe
        base_path = os.path.join(os.getcwd(), 'backend', UPLOAD_FOLDER)
        os.makedirs(base_path, exist_ok=True)
        
        # Generar nombre único para el archivo
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{event_id}_{uuid.uuid4().hex}.{file_extension}"
        file_path = os.path.join(base_path, unique_filename)
        
        # Guardar el archivo
        file.save(file_path)
        
        # Si el evento ya tenía una imagen, eliminar la anterior
        if event.image_url:
            old_filename = event.image_url.split('/')[-1]
            old_path = os.path.join(base_path, old_filename)
            if os.path.exists(old_path):
                try:
                    os.remove(old_path)
                except Exception as e:
                    print(f"Error al eliminar imagen anterior: {e}")
        
        # Actualizar la URL de la imagen en el evento
        event.image_url = f"/uploads/events/{unique_filename}"
        event.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Imagen subida exitosamente',
            'image_url': event.image_url,
            'filename': unique_filename
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al subir imagen: {str(e)}'}), 500

@upload_bp.route('/api/v1/events/<int:event_id>/remove-image', methods=['DELETE'])
@jwt_required()
@role_required(['admin', 'staff'])
def remove_event_image(event_id):
    """Eliminar imagen de portada de un evento"""
    try:
        # Verificar que el evento existe
        event = Event.query.get_or_404(event_id)
        
        if not event.image_url:
            return jsonify({'error': 'El evento no tiene imagen'}), 400
        
        # Obtener el path del archivo
        filename = event.image_url.split('/')[-1]
        base_path = os.path.join(os.getcwd(), 'backend', UPLOAD_FOLDER)
        file_path = os.path.join(base_path, filename)
        
        # Eliminar el archivo si existe
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error al eliminar archivo: {e}")
        
        # Actualizar la base de datos
        event.image_url = None
        event.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Imagen eliminada exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al eliminar imagen: {str(e)}'}), 500
