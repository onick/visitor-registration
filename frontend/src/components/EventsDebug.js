// EventsDebug.js
// Script para verificar que los eventos se estén cargando correctamente

// Función para verificar eventos
export function checkEvents(events, upcomingEvents, ongoingEvents) {
  console.log('======= DIAGNÓSTICO DE EVENTOS =======');
  console.log(`Total de eventos en estado (sin filtrar): ${events.length}`);
  
  // Verificar eventos activos
  const activeEvents = events.filter(event => event.isActive || event.is_active);
  console.log(`Eventos activos: ${activeEvents.length}`);
  
  // Verificar eventos inactivos
  const inactiveEvents = events.filter(event => !(event.isActive || event.is_active));
  console.log(`Eventos inactivos: ${inactiveEvents.length}`);
  
  // Verificar próximos eventos
  console.log(`Próximos eventos: ${upcomingEvents.length}`);
  
  // Verificar eventos en curso
  console.log(`Eventos en curso: ${ongoingEvents.length}`);
  
  // Verificar si hay problemas con las fechas
  let badDateFormat = 0;
  for (const event of events) {
    const startDate = new Date(event.startDate || event.start_date);
    const endDate = new Date(event.endDate || event.end_date);
    
    if (isNaN(startDate.getTime()) || isNaN(endDate.getTime())) {
      badDateFormat++;
      console.error(`Evento con formato de fecha incorrecto:`, event);
    }
  }
  
  console.log(`Eventos con problemas de formato de fecha: ${badDateFormat}`);
  console.log('====================================');
  
  return {
    totalEvents: events.length,
    activeEvents: activeEvents.length,
    inactiveEvents: inactiveEvents.length,
    upcomingEvents: upcomingEvents.length,
    ongoingEvents: ongoingEvents.length,
    badDateFormat
  };
}
