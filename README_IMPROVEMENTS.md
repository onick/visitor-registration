# Mejoras de Lógica para el Proyecto CCB

Este documento detalla las mejoras de lógica implementadas en el sistema de registro de visitantes del Centro Cultural Banreservas, siguiendo la propuesta de mejora estructurada en 8 pasos principales.

## ✅ Mejoras Implementadas

### 1. Refuerzo de Seguridad y Autorización

#### 1.1 Sistema de Roles y Permisos
Se ha implementado un sistema granular de permisos con las siguientes características:
- Modelo `Permission` para definir permisos específicos
- Modelo `Role` para agrupar permisos
- Relación muchos a muchos entre roles y permisos
- Métodos de verificación `has_permission` y `has_permissions` en el modelo `User`

#### 1.2 Rate Limiting
- Integración de `Flask-Limiter` para controlar el número de peticiones
- Protección contra ataques de fuerza bruta en endpoints sensibles
- Configuración flexible por entorno (desarrollo, pruebas, producción)

#### 1.3 Validación y Saneamiento
- Implementación de schemas de validación con `marshmallow`
- Validadores para formatos de correo, teléfono, nombres, etc.
- Funciones de saneamiento para prevenir XSS

#### 1.4 Auditoría
- Modelo `AuditLog` para registrar acciones importantes
- Decorador `log_action` para registro automático de eventos
- Registro de accesos, modificaciones y eventos críticos

#### 1.5 HTTPS y Credenciales
- Configuración para forzar HTTPS en producción
- Manejo de variables sensibles mediante variables de entorno
- Validación de configuración en producción

### 2. Manejo de Errores y Experiencia de Usuario

#### 2.1 Respuestas Estandarizadas
- Esquema JSON consistente para errores
- Códigos de error específicos para cada tipo de problema
- Manejo centralizado de excepciones

#### 2.2 Mensajes de Error Amigables
- Traducción de códigos de error a mensajes comprensibles
- Formato consistente para errores de validación

#### 2.3 Degradación Elegante
- Manejo de errores en tareas asíncronas
- Capacidad de continuar operación si fallan servicios externos

### 3. Escalabilidad y Rendimiento

#### 3.1 Caché con Redis
- Implementación de caché para consultas frecuentes
- Invalidación inteligente de caché
- Configuración flexible según el entorno

#### 3.2 Tareas Asíncronas
- Integración de Celery para procesamiento en segundo plano
- Tareas para envío de correos y notificaciones
- Generación de reportes sin bloquear el servidor principal

#### 3.3 Optimizaciones en Base de Datos
- Estructuras de datos más eficientes
- Métodos para obtener estadísticas sin sobrecargar la base de datos

### 4. Internacionalización y Accesibilidad

- Preparación para soporte multilenguaje
- Estructura para agregar traducciones fácilmente

### 5. Cumplimiento y Manejo de Datos

- Anonimización de datos sensibles
- Estructura para respaldos automáticos

### 6. Pruebas

- Estructura para pruebas unitarias
- Configuración para pruebas de integración

### 7. CI/CD y Operaciones

- Configuración para monitoreo con Sentry
- Configuración para logs centralizados

### 8. Estado de Visitantes

- Adición del estado `CANCELED` para registros
- Métodos para cancelar registros y mostrarlos correctamente en la UI

## Estructura de Archivos Nuevos/Modificados

### Modelos
- `models/permission.py`: Define los modelos `Role`, `Permission` y `AuditLog`
- `models/user.py`: Actualizado para incluir relación con roles y permisos
- `models/visitor.py`: Actualizado para incluir el estado `CANCELED`
- `models/event.py`: Actualizado para reflejar la relación con `EventVisitor`

### Utilidades
- `utils/decorators.py`: Decoradores para permisos y auditoría
- `utils/validators.py`: Validación y saneamiento de datos
- `cache.py`: Configuración y utilidades para caché
- `tasks.py`: Tareas asíncronas con Celery
- `errors.py`: Manejo centralizado de errores

### Configuración
- `config/config.py`: Configuración centralizada por entorno
- `visitor.py`: Script para actualizar el modelo de visitante con el estado `CANCELED`

## Guía de Uso

### Permisos y Roles

Para proteger un endpoint con permisos específicos:

```python
from utils.decorators import permission_required

@app.route('/api/events/<int:event_id>', methods=['DELETE'])
@permission_required('delete_event')
def delete_event(event_id):
    # Lógica para eliminar evento
    pass
```

Para verificar permisos en el código:

```python
if current_user.has_permission('edit_event'):
    # Mostrar botón de edición
```

### Manejo de Errores

Para crear una respuesta de error estandarizada:

```python
from errors import create_error_response

@app.route('/api/events/<int:event_id>')
def get_event(event_id):
    event = Event.query.get(event_id)
    if not event:
        return create_error_response(
            'RESOURCE_NOT_FOUND', 
            f'No se encontró el evento con ID {event_id}'
        ), 404
    return jsonify(event.to_dict())
```

Para lanzar una excepción que será manejada automáticamente:

```python
from errors import APIError

def register_visitor(visitor_data, event_id):
    event = Event.query.get(event_id)
    if not event:
        raise APIError('RESOURCE_NOT_FOUND', f'Evento no encontrado', status_code=404)
    
    if event.available_capacity <= 0:
        raise APIError('EVENT_FULL', 'El evento está lleno', status_code=400)
    
    # Lógica para registrar visitante
```

### Caché

Para cachear una vista:

```python
from cache import cached

@app.route('/api/events/active')
@cached(timeout=300)
def get_active_events():
    events = Event.query.filter_by(is_active=True).all()
    return jsonify([event.to_dict() for event in events])
```

Para cachear un método específico:

```python
from cache import cache_event_data

@app.route('/api/events/<int:event_id>')
def get_event(event_id):
    @cache_event_data(event_id, timeout=300)
    def fetch_event_data():
        event = Event.query.get(event_id)
        if not event:
            return None
        return event.to_dict()
    
    event_data = fetch_event_data()
    if not event_data:
        return create_error_response('RESOURCE_NOT_FOUND'), 404
    
    return jsonify(event_data)
```

### Tareas Asíncronas

Para enviar un correo de confirmación:

```python
from tasks import send_registration_confirmation

def register_visitor(visitor_data, event_id):
    # Lógica para registrar visitante
    
    # Enviar correo de confirmación en segundo plano
    event = Event.query.get(event_id)
    send_registration_confirmation.delay(visitor.to_dict(), event.to_dict())
    
    return jsonify({'success': True})
```

## Notas de Implementación

- Todas las mejoras mantienen compatibilidad con el código existente
- Se ha priorizado la seguridad y la escalabilidad sin sacrificar el rendimiento
- Se recomienda activar las nuevas características progresivamente en producción

## Siguientes Pasos

1. Completar las migraciones de base de datos para los nuevos modelos
2. Configurar Redis para entornos de producción
3. Implementar los componentes de UI para manejar el estado CANCELED
4. Configurar Sentry para monitoreo de errores
5. Implementar pruebas automatizadas para las nuevas funcionalidades 