# Sistema de Registro de Visitantes - Centro Cultural Banreservas

## Funcionalidades Actualizadas

### 1. Tarjetas de Eventos con Conteos
Las tarjetas en la vista de gestión de eventos ahora muestran:
- 👤 Número de registrados
- 👥 Número de asistentes

### 2. Vista de Detalles del Evento
Al hacer clic en "Ver Detalles" en cualquier tarjeta de evento, se muestra:

#### Información General
- Título del evento
- Fechas y horarios
- Ubicación
- Descripción
- Estado (En curso, Próximo, Finalizado)

#### Estadísticas en Tiempo Real
- Total de visitantes registrados
- Total de check-ins realizados
- Tasa de asistencia (porcentaje)

#### Lista de Visitantes
- Tabla completa con todos los registrados
- Búsqueda en tiempo real
- Estado de cada visitante
- Acciones de check-in

## Cómo Usar

### 1. Ver Eventos
1. Inicia sesión en el panel de administración
2. Ve a "Gestión de Eventos" en el menú lateral
3. Verás todas las tarjetas de eventos con sus conteos

### 2. Ver Detalles de un Evento
1. En cualquier tarjeta de evento, haz clic en "Ver Detalles"
2. Se abrirá la vista completa con toda la información
3. Usa la barra de búsqueda para encontrar visitantes específicos
4. Realiza check-ins directamente desde la lista

### 3. Navegación
- Usa el botón "Volver" para regresar a la lista de eventos
- Los breadcrumbs muestran tu ubicación actual

## Arquitectura Técnica

### Backend (Flask)
- `GET /api/v1/events/` - Lista de eventos con conteos
- `GET /api/v1/events/:id` - Detalles del evento con estadísticas
- `GET /api/v1/visitors/event/:id` - Visitantes de un evento
- `POST /api/v1/events/:id/visitors/:id/checkin` - Realizar check-in

### Frontend (Vue.js)
- Store Vuex para gestión de estado
- Componentes reutilizables
- Actualización en tiempo real
- Diseño responsive

## Ejecutar el Proyecto

### Backend
```bash
cd backend
source venv/bin/activate  # Mac/Linux
python app.py
```

### Frontend
```bash
cd frontend
npm install
npm run serve
```

## Tests

### Test de Tarjetas de Eventos
1. Abre el navegador en `/admin/events`
2. Abre la consola del desarrollador (F12)
3. Ejecuta el contenido de `tests/frontend/test_event_cards_counts.js`

### Test de Vista de Detalles
1. Abre el navegador en `/admin/events/:id`
2. Abre la consola del desarrollador (F12)
3. Ejecuta el contenido de `tests/frontend/test_event_details_view.js`

## Próximas Funcionalidades

1. Exportación de visitantes a CSV/Excel
2. Gráficos de estadísticas
3. Edición inline de eventos
4. Sistema de notificaciones en tiempo real
5. Historial de cambios

## Solución de Problemas

### Los conteos no se muestran
1. Verifica que el backend esté devolviendo `registered_count` y `checked_in_count`
2. Revisa el mapeo en el store de Vuex
3. Ejecuta los tests para diagnosticar

### Error al cargar detalles
1. Verifica la conexión con el backend
2. Revisa los permisos del usuario
3. Verifica que el ID del evento sea válido

## Documentación

- [Conteos en Tarjetas](docs/FEATURE_EVENT_COUNTS.md)
- [Vista de Detalles](docs/FEATURE_EVENT_DETAILS.md)
- [API Reference](docs/API.md)
