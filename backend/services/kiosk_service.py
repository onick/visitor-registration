"""
Servicio para la gestión de kioscos
"""
from models.kiosk import Kiosk, KioskConfig
from models.database import db
from datetime import datetime

class KioskService:
    """
    Clase de servicio para operaciones relacionadas con kioscos
    """
    
    @staticmethod
    def get_all_kiosks():
        """
        Obtener todos los kioscos
        """
        return Kiosk.query.all()
    
    @staticmethod
    def get_kiosk_by_id(kiosk_id):
        """
        Obtener un kiosco por su ID
        """
        return Kiosk.query.get(kiosk_id)
    
    @staticmethod
    def create_kiosk(kiosk_data):
        """
        Crear un nuevo kiosco
        """
        kiosk = Kiosk(
            name=kiosk_data.get('name'),
            location=kiosk_data.get('location'),
            is_active=kiosk_data.get('is_active', True)
        )
        
        db.session.add(kiosk)
        db.session.commit()
        
        # Crear configuración por defecto para el kiosco
        config = KioskConfig(
            kiosk_id=kiosk.id,
            language=kiosk_data.get('language', 'es'),
            idle_timeout=kiosk_data.get('idle_timeout', 60),
            event_filter=kiosk_data.get('event_filter'),
            custom_message=kiosk_data.get('custom_message')
        )
        
        db.session.add(config)
        db.session.commit()
        
        return kiosk
    
    @staticmethod
    def update_kiosk(kiosk_id, kiosk_data):
        """
        Actualizar un kiosco existente
        """
        kiosk = Kiosk.query.get(kiosk_id)
        
        if not kiosk:
            return None
        
        # Actualizar solo los campos proporcionados
        if 'name' in kiosk_data:
            kiosk.name = kiosk_data['name']
        if 'location' in kiosk_data:
            kiosk.location = kiosk_data['location']
        if 'is_active' in kiosk_data:
            kiosk.is_active = kiosk_data['is_active']
        
        db.session.commit()
        return kiosk
    
    @staticmethod
    def update_kiosk_config(kiosk_id, config_data):
        """
        Actualizar la configuración de un kiosco
        """
        config = KioskConfig.query.filter_by(kiosk_id=kiosk_id).first()
        
        if not config:
            # Si no existe la configuración, crearla
            config = KioskConfig(kiosk_id=kiosk_id)
            db.session.add(config)
        
        # Actualizar solo los campos proporcionados
        if 'language' in config_data:
            config.language = config_data['language']
        if 'idle_timeout' in config_data:
            config.idle_timeout = config_data['idle_timeout']
        if 'event_filter' in config_data:
            config.event_filter = config_data['event_filter']
        if 'custom_message' in config_data:
            config.custom_message = config_data['custom_message']
        if 'logo_url' in config_data:
            config.logo_url = config_data['logo_url']
        
        db.session.commit()
        return config
    
    @staticmethod
    def get_kiosk_config(kiosk_id):
        """
        Obtener la configuración de un kiosco
        """
        return KioskConfig.query.filter_by(kiosk_id=kiosk_id).first()
    
    @staticmethod
    def update_heartbeat(kiosk_id):
        """
        Actualizar el último heartbeat de un kiosco
        """
        kiosk = Kiosk.query.get(kiosk_id)
        
        if not kiosk:
            return None
        
        kiosk.last_heartbeat = datetime.utcnow()
        db.session.commit()
        
        return {
            'status': 'ok',
            'timestamp': kiosk.last_heartbeat
        }
    
    @staticmethod
    def get_online_kiosks():
        """
        Obtener todos los kioscos que están en línea
        """
        # Un kiosco se considera en línea si su último heartbeat fue hace menos de 5 minutos
        five_minutes_ago = datetime.utcnow() - datetime.timedelta(minutes=5)
        
        return Kiosk.query.filter(
            Kiosk.is_active == True,
            Kiosk.last_heartbeat >= five_minutes_ago
        ).all()
