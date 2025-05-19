# Vista de Detalles del Evento

## Descripción

La vista de detalles del evento muestra información completa sobre un evento específico, incluyendo:
- Información general del evento
- Estadísticas de asistencia
- Lista de visitantes registrados
- Estado de check-in de cada visitante

## Acceso

Para acceder a la vista de detalles de un evento:
1. Ir a la página de Gestión de Eventos (`/admin/events`)
2. Hacer clic en el botón "Ver Detalles" en cualquier tarjeta de evento
3. O navegar directamente a `/admin/events/:id` donde `:id` es el ID del evento

## Estructura de la Vista

### 1. Encabezado
- Botón "Volver" para regresar a la lista de eventos
- Título "Detalles del Evento"

### 2. Información del Evento
- Título del evento
- Badge de estado (En curso, Próximo, Finalizado)
- Botón "Editar" para modificar el evento

### 3. Tarjeta de Información General
Muestra todos los detalles del evento:
- Título
- Fecha y hora de inicio
- Fecha y hora de finalización
- Ubicación
- Estado actual
- Descripción
- Fecha de creación
- Última actualización

### 4. Tarjeta de Estadísticas
Muestra métricas clave del evento:
- 👥 Visitantes registrados
- ✓ Check-ins completados
- % Tasa de asistencia

### 5. Sección de Visitantes Registrados
Lista todos los visitantes del evento con:
- Barra de búsqueda para filtrar visitantes
- Botón de exportar (para descargar la lista)
- Tabla con información de cada visitante:
  - Nombre
  - Email
  - Teléfono
  - Fecha de registro
  - Estado (Registrado/Check-in completado)
  - Acciones (check-in, ver detalles)

## Funcionalidades

### Búsqueda de Visitantes
- Busca en tiempo real por nombre, email o teléfono
- Filtrado instantáneo sin recarga de página

### Check-in de Visitantes
- Botón de check-in disponible para visitantes registrados
- Se deshabilita automáticamente después del check-in
- Actualiza las estadísticas en tiempo real

### Exportar Visitantes
- Permite descargar la lista de visitantes (función por implementar)

## Datos Mostrados

### Del Backend
```json
{
  "id": 1,
  "title": "Nombre del Evento",
  "description": "Descripción",
  "start_date": "2025-05-20T18:00:00",
  "end_date": "2025-05-20T20:00:00",
  "location": "Ubicación",
  "is_active": true,
  "registered_count": 10,
  "checked_in_count": 5
}
```

### Mapeo en Frontend
- `title` → `name`
- `start_date` → `startDate`
- `end_date` → `endDate`
- `registered_count` → `registeredCount`
- `checked_in_count` → `checkedInCount`

## Estados de la Vista

### 1. Cargando
- Muestra spinner mientras carga los datos

### 2. Error
- Muestra mensaje de error si falla la carga
- Botón para reintentar

### 3. Vacío
- Si no se encuentra el evento
- Botón para volver a la lista

### 4. Con Datos
- Muestra toda la información del evento

## Responsive Design

La vista se adapta a diferentes tamaños de pantalla:
- **Desktop**: Tarjetas lado a lado
- **Tablet**: Tarjetas apiladas
- **Móvil**: Diseño vertical completo

## Próximas Mejoras

1. Implementar edición inline de eventos
2. Agregar gráficos de estadísticas
3. Funcionalidad real de exportación
4. Historial de cambios del evento
5. Sistema de notificaciones en tiempo real
