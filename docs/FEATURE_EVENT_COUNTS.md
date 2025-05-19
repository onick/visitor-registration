# Actualización: Conteo de Registrados en Tarjetas de Eventos

## Cambios Realizados

### Backend
1. Actualizado el endpoint `/api/v1/events/` para incluir los campos:
   - `registered_count`: Número de visitantes registrados para el evento
   - `checked_in_count`: Número de visitantes que hicieron check-in

### Frontend
1. Actualizado el store de Vuex (`events.js`) para mapear correctamente los nuevos campos
2. Las mutaciones `SET_EVENTS`, `ADD_EVENT` y `UPDATE_EVENT` ahora incluyen los conteos
3. Las tarjetas de eventos en la vista de administración ya muestran los conteos

## Cómo Verificar los Cambios

### 1. Ejecutar el Backend
```bash
cd backend
# Activar el entorno virtual si es necesario
source venv/bin/activate  # En Mac/Linux
# o
venv\Scripts\activate  # En Windows

# Ejecutar el servidor
python app.py
```

### 2. Ejecutar el Frontend
```bash
cd frontend
npm install  # Si es necesario
npm run serve
```

### 3. Ejecutar Tests

#### Test del Backend (desde la terminal):
```bash
cd backend
python test_event_counts.py
```
Este test verificará que el backend está devolviendo los conteos correctamente.

#### Test del Frontend (desde el navegador):
1. Abre el navegador y ve a `http://localhost:8080/admin/events`
2. Abre la consola del desarrollador (F12)
3. Copia y pega el contenido del archivo `tests/frontend/test_event_cards_counts.js`
4. Presiona Enter para ejecutar el test

El test verificará que:
- Los eventos en el store tienen los campos de conteo
- Las tarjetas en el DOM muestran los conteos
- El backend está devolviendo los datos correctamente

## Estructura de las Tarjetas

Las tarjetas de eventos ahora muestran:
```
📅 [Fecha]
[Nombre del Evento]
⏰ [Hora]
📍 [Ubicación]
[Descripción]

👤 X registrados    👥 Y asistentes
```

## Notas Importantes

1. Los conteos se calculan en tiempo real basándose en la tabla `VisitorCheckIn`
2. Por ahora, `checked_in_count` es igual a `registered_count` (todos los registrados se consideran con check-in)
3. Si no hay registros para un evento, ambos conteos serán 0

## Próximos Pasos Sugeridos

1. Implementar un campo real de check-in en la tabla `VisitorCheckIn` para diferenciar entre registrados y asistentes
2. Agregar filtros en la vista de eventos por número de registrados
3. Implementar gráficos o visualizaciones de los conteos
4. Agregar exportación de datos con los conteos incluidos
