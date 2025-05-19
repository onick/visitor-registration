// Script de prueba para verificar que los eventos activos se muestran correctamente

// Ejecuta este script desde la consola del navegador cuando estés en la aplicación

// 1. Verificar el store de eventos
console.log('=== Verificando eventos en el store ===');
const store = window.$app.$store || window.app.$store;

if (store) {
  const state = store.state.events;
  console.log('Todos los eventos:', state.events);
  console.log('Eventos activos (getter):', store.getters['events/activeEvents']);
  console.log('Eventos activos (filtrados):', store.getters['events/allEvents']);
  
  // Verificar cada evento
  state.events.forEach(event => {
    console.log(`Evento: ${event.name || event.title}`);
    console.log(`  - is_active: ${event.is_active}`);
    console.log(`  - isActive: ${event.isActive}`);
    console.log(`  - Estado real: ${event.isActive || event.is_active ? 'ACTIVO' : 'INACTIVO'}`);
  });
} else {
  console.error('No se pudo acceder al store. Asegúrate de estar en la aplicación.');
}

// 2. Verificar la vista actual
console.log('\n=== Verificando vista actual ===');
const currentRoute = window.$app.$route || window.app.$route;
if (currentRoute) {
  console.log('Ruta actual:', currentRoute.path);
  console.log('Componente:', currentRoute.matched[0]?.components?.default?.name);
}

// 3. Verificar componente de lista de eventos
const eventListComponent = document.querySelector('.events-list');
if (eventListComponent) {
  console.log('\n=== Lista de eventos en el DOM ===');
  const eventCards = document.querySelectorAll('.event-card, [class*="event"]');
  console.log(`Número de eventos mostrados: ${eventCards.length}`);
  
  eventCards.forEach((card, index) => {
    const eventName = card.querySelector('.event-name, h3')?.textContent;
    const statusBadge = card.querySelector('.status-badge');
    console.log(`${index + 1}. ${eventName} - Estado: ${statusBadge?.textContent || 'No definido'}`);
  });
}

console.log('\n=== Recomendaciones ===');
console.log('1. Si no ves eventos activos, verifica que el campo is_active esté configurado en true en la base de datos');
console.log('2. Puedes crear un evento de prueba activo desde el panel administrativo');
console.log('3. Asegúrate de recargar la página después de hacer cambios');
