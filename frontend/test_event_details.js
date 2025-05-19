// Script de prueba para verificar la funcionalidad de Ver Detalles

// Este script verifica que:
// 1. La navegación a EventDetails funcione correctamente
// 2. Los datos del evento se carguen correctamente
// 3. Los visitantes registrados se muestren en la vista

// Para usar este script:
// 1. Abre la aplicación en el navegador
// 2. Ve a la sección de Eventos del panel administrativo
// 3. Haz clic en "Ver Detalles" de cualquier evento
// 4. Abre la consola del navegador (F12)
// 5. Copia y pega este código en la consola

// Verificar que estamos en la vista correcta
if (window.location.pathname.includes('/admin/events/')) {
    console.log('✅ Estás en la vista de detalles del evento');
    
    // Verificar el ID del evento
    const eventId = window.location.pathname.split('/').pop();
    console.log('ID del evento:', eventId);
    
    // Verificar el componente Vue
    const app = document.querySelector('#app').__vue_app__;
    const rootComponent = app._instance.proxy;
    console.log('Componente Vue encontrado:', !!rootComponent);
    
    // Verificar los datos del evento
    const vm = rootComponent.$children.find(child => child.$options.name === 'EventDetails');
    if (vm) {
        console.log('✅ Componente EventDetails encontrado');
        console.log('Datos del evento:', vm.event);
        console.log('Visitantes:', vm.visitors);
        console.log('Estadísticas:', vm.eventStats);
    } else {
        console.log('❌ No se encontró el componente EventDetails');
        console.log('Componentes disponibles:', rootComponent.$children.map(c => c.$options.name));
    }
    
    // Verificar la store de Vuex
    const store = rootComponent.$store;
    const eventState = store.state.events;
    console.log('Estado de eventos en Vuex:', eventState);
    console.log('Evento actual:', eventState.currentEvent);
    
} else {
    console.log('❌ No estás en la vista de detalles del evento');
    console.log('Para probar esta funcionalidad:');
    console.log('1. Ve a /admin/events');
    console.log('2. Haz clic en "Ver Detalles" de cualquier evento');
    console.log('3. Ejecuta este script nuevamente');
}

// Función para simular clic en Ver Detalles
function simularClickVerDetalles() {
    const botones = document.querySelectorAll('.btn-text');
    const botonVerDetalles = Array.from(botones).find(btn => btn.textContent.includes('Ver Detalles'));
    
    if (botonVerDetalles) {
        console.log('✅ Botón "Ver Detalles" encontrado, haciendo clic...');
        botonVerDetalles.click();
    } else {
        console.log('❌ No se encontró el botón "Ver Detalles"');
        console.log('Botones disponibles:', Array.from(botones).map(btn => btn.textContent));
    }
}

// Si estamos en la lista de eventos, podemos simular el clic
if (window.location.pathname === '/admin/events') {
    console.log('📍 Estás en la lista de eventos');
    console.log('Ejecuta simularClickVerDetalles() para hacer clic en el primer evento');
}
