# Inicializar paquete de endpoints
from .auth import auth_namespace
from .events import events_namespace
from .visitors import visitors_namespace
from .kiosks import kiosks_namespace
from .notifications import notifications_namespace

# Lista de todos los namespaces disponibles
namespaces = [
    auth_namespace,
    events_namespace,
    visitors_namespace,
    kiosks_namespace,
    notifications_namespace
]
