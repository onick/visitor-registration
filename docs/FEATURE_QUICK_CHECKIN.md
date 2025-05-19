# Sistema de Check-in Rápido

## Descripción

El sistema de check-in rápido permite a los visitantes que ya están en la base de datos hacer check-in a eventos mostrando únicamente su código de registro, sin necesidad de volver a introducir sus datos personales.

## Cómo Funciona

### 1. Tipos de Códigos Aceptados
Los visitantes pueden usar cualquiera de estos códigos:
- **ID numérico**: El ID único del visitante (ej: 1, 2, 3)
- **Email**: Su dirección de correo electrónico completa
- **Teléfono**: Su número de teléfono registrado

### 2. Flujo de Check-in

#### Paso 1: Ingreso del Código
- El visitante puede escanear un código QR o ingresar manualmente su código
- El sistema acepta múltiples formatos de identificación

#### Paso 2: Verificación
- El sistema busca al visitante en la base de datos
- Si se encuentra, muestra los eventos activos para los que está registrado

#### Paso 3: Selección de Evento
- Si el visitante tiene múltiples eventos activos, puede seleccionar a cuál hacer check-in
- Si solo tiene un evento activo, el sistema procede automáticamente

#### Paso 4: Confirmación
- Se muestra una pantalla de éxito con los detalles del check-in
- El visitante puede hacer check-in a otros eventos si tiene más disponibles

## Características Técnicas

### Backend

#### Nuevo Endpoint: `/api/v1/visitors/verify-code`
```python
POST /api/v1/visitors/verify-code
{
    "code": "identificador_del_visitante"
}
```

**Respuesta exitosa:**
```json
{
    "visitor": {
        "id": 1,
        "name": "Juan Pérez",
        "email": "juan@ejemplo.com",
        "phone": "809-555-0001"
    },
    "events": [
        {
            "id": 1,
            "title": "Concierto de Jazz",
            "start_date": "2025-05-20T18:00:00",
            "end_date": "2025-05-20T21:00:00",
            "location": "Auditorio Principal",
            "registration_id": 1,
            "checked_in": false
        }
    ]
}
```

### Frontend

#### Componente CheckinView.vue
Actualizado para soportar el flujo de check-in rápido con:
- Entrada de código manual
- Listado de eventos disponibles
- Proceso de check-in por evento
- Manejo de estados (cargando, éxito, error)

## Seguridad

1. **Validación de Códigos**: El sistema valida que el código corresponda a un visitante real
2. **Eventos Activos**: Solo muestra eventos que están actualmente activos
3. **Prevención de Duplicados**: No permite check-in múltiples al mismo evento

## Casos de Uso

### Caso 1: Visitante con un Solo Evento
1. Ingresa su código (ID, email o teléfono)
2. El sistema lo identifica y hace check-in automáticamente
3. Muestra confirmación de éxito

### Caso 2: Visitante con Múltiples Eventos
1. Ingresa su código
2. Ve una lista de eventos disponibles
3. Selecciona el evento para check-in
4. Puede repetir para otros eventos

### Caso 3: Código Inválido
1. Ingresa un código no registrado
2. El sistema muestra un mensaje de error
3. Puede intentar con otro código

## Configuración

### Base de Datos
Los visitantes deben tener al menos uno de estos campos:
- `id` (integer, primary key)
- `email` (string, unique)
- `phone` (string)

### Eventos
Los eventos deben tener:
- `is_active` = true
- `start_date` <= fecha/hora actual
- `end_date` >= fecha/hora actual

## Testing

### Crear Visitantes de Prueba
```bash
cd backend
python create_test_visitors.py
```

### Test del Frontend
1. Navegar a `/kiosk/checkin`
2. Abrir consola del navegador
3. Ejecutar el contenido de `tests/frontend/test_quick_checkin.js`

### Códigos de Prueba
Después de ejecutar el script de creación:
- IDs: 1, 2, 3, 4, 5
- Emails: juan.perez@ejemplo.com, maria.garcia@ejemplo.com, etc.
- Teléfonos: 809-555-0001, 809-555-0002, etc.

## Mejoras Futuras

1. **Códigos QR Personalizados**: Generar QR únicos por visitante
2. **Check-in por Reconocimiento Facial**: Integración con cámaras
3. **Notificaciones**: Enviar confirmación por email/SMS
4. **Historial**: Ver historial de check-ins anteriores
5. **Integración con Apps**: Check-in desde aplicación móvil
