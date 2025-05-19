// Script para verificar el dashboard corregido
// Ejecutar desde la consola del navegador

console.log('=== VERIFICACIÓN DEL DASHBOARD ===');

// Función para esperar
const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function verificarDashboard() {
    const store = window.$app?.$store || window.app?.$store;
    
    if (!store) {
        console.error('No se pudo acceder al store');
        return;
    }
    
    console.log('\n1. Estado del store:');
    
    // Eventos
    console.log('\n📊 Estadísticas de Eventos:');
    const eventStats = store.getters['events/statistics'];
    console.log('   Total:', eventStats?.total || 0);
    console.log('   Activos:', eventStats?.active || 0);
    console.log('   Próximos:', eventStats?.upcoming || 0);
    
    // Visitantes
    console.log('\n👥 Estadísticas de Visitantes:');
    const visitorStats = store.state.visitors?.statistics || {};
    console.log('   Total:', visitorStats.total || 0);
    console.log('   Check-ins:', visitorStats.checkedIn || 0);
    console.log('   Hoy:', visitorStats.today || 0);
    
    console.log('\n2. Elementos del DOM:');
    
    // Tarjetas
    const statCards = document.querySelectorAll('.stat-card');
    console.log(`   ✓ ${statCards.length} tarjetas de estadísticas`);
    
    // Gráficos
    await wait(500); // Esperar que se rendericen
    const canvasElements = document.querySelectorAll('canvas');
    console.log(`   ✓ ${canvasElements.length} elementos canvas`);
    
    // Verificar si hay errores
    const errorElements = document.querySelectorAll('.no-data');
    if (errorElements.length > 0) {
        console.log(`   ⚠️  ${errorElements.length} secciones sin datos`);
    }
    
    // Verificar componentes de carga
    const loadingElements = document.querySelectorAll('.loading-chart');
    if (loadingElements.length > 0) {
        console.log(`   ⏳ ${loadingElements.length} componentes cargando`);
    }
    
    console.log('\n3. Para actualizar datos manualmente:');
    console.log('   await store.dispatch("events/fetchStatistics")');
    console.log('   await store.dispatch("visitors/fetchStatistics")');
    
    return true;
}

// Ejecutar verificación
verificarDashboard();
