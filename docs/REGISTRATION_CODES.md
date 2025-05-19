# Sistema de Códigos de Registro

## Descripción General

El sistema de registro de visitantes del Centro Cultural Banreservas ahora genera códigos únicos alfanuméricos de 6 caracteres para cada visitante registrado. Estos códigos facilitan el proceso de check-in y mejoran la experiencia del usuario.

## Características del Código

- **Formato**: 6 caracteres alfanuméricos (mayúsculas y números)
- **Único**: Cada código es único en el sistema
- **Generación automática**: Se genera automáticamente al registrar un visitante
- **Métodos de verificación múltiples**: Los visitantes pueden hacer check-in usando:
  - Código de registro único
  - Email
  - Teléfono
  - ID numérico del visitante

## Implementación Técnica

### Modelo de Base de Datos

Se agregó un campo `registration_code` a la tabla `visitors`:

```python
class Visitor(db.Model):
    # ... otros campos ...
    registration_code = db.Column(db.String(10), unique=True, nullable=False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.registration_code:
            self.registration_code = self.generate_unique_code()
```

### Generación de Códigos

El método `generate_unique_code()` asegura que cada código sea único:

```python
@staticmethod
def generate_unique_code():
    """Genera un código único de 6 caracteres alfanuméricos"""
    characters = string.ascii_uppercase + string.digits
    while True:
        code = ''.join(secrets.choice(characters) for _ in range(6))
        # Verificar que el código no exista
        if not Visitor.query.filter_by(registration_code=code).first():
            return code
```

### API Endpoints

#### Registro de Visitante
- **Endpoint**: `POST /api/v1/visitors/register`
- **Respuesta**: Incluye el código de registro

```json
{
    "success": true,
    "message": "Visitante registrado exitosamente",
    "visitor_id": 123,
    "registration_code": "ABC123",
    "checkin_id": 456
}
```

#### Verificación de Código
- **Endpoint**: `POST /api/v1/visitors/verify-code`
- **Request**:
```json
{
    "code": "ABC123"
}
```
- **Respuesta**:
```json
{
    "visitor": {
        "id": 123,
        "name": "María González",
        "email": "maria@example.com",
        "phone": "809-555-1234"
    },
    "events": [
        {
            "id": 1,
            "title": "Recital de Poesía",
            "location": "Sala Principal",
            "start_date": "2025-05-20T18:00:00"
        }
    ]
}
```

## Flujo de Usuario

1. **Registro**: El visitante se registra para un evento
2. **Generación**: El sistema genera automáticamente un código único
3. **Confirmación**: El código se muestra en pantalla y se puede enviar por email
4. **Check-in**: El visitante puede usar cualquiera de estos métodos:
   - Ingresar su código de 6 caracteres
   - Escanear un código QR (futuro)
   - Usar su email o teléfono

## Migración de Base de Datos

Para visitantes existentes, ejecutar el script de migración:

```bash
cd backend
python add_registration_code.py
```

Este script:
- Agrega la columna `registration_code` si no existe
- Genera códigos únicos para todos los visitantes existentes
- Asegura que no haya códigos duplicados

## Pruebas

Ejecutar el script de prueba para verificar el funcionamiento:

```bash
cd backend
python test_registration_codes.py
```

Este script prueba:
- Registro de nuevo visitante con código
- Verificación con código único
- Verificación con email
- Verificación con teléfono
- Manejo de códigos inválidos

## Consideraciones de Seguridad

- Los códigos se generan usando `secrets` para mayor seguridad
- Los códigos son únicos y no secuenciales
- Se mantiene compatibilidad con métodos de verificación anteriores
- Los códigos son case-insensitive para facilitar el ingreso

## Próximas Mejoras

1. **Códigos QR**: Generar códigos QR con el código de registro
2. **Notificaciones**: Enviar código por email después del registro
3. **Personalización**: Permitir configurar formato y longitud del código
4. **Expiración**: Agregar fecha de expiración opcional a los códigos
5. **Bulk Generation**: Generar códigos en lote para eventos especiales
