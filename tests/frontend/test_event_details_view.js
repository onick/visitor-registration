/**
 * Test para verificar que la vista de detalles del evento muestra correctamente
 * la información del evento, los registrados y asistentes.
 * 
 * Este test se ejecuta en el navegador desde la consola del desarrollador
 */

async function testEventDetailsView() {
    console.log('=== Test: Vista de Detalles del Evento ===');
    
    try {
        // 1. Verificar que estamos en la página de detalles del evento
        if (!window.location.pathname.includes('/admin/events/')) {
            console.log('Navegando a un evento para probar...');
            
            // Obtener el primer evento disponible
            const store = document.querySelector('#app').__vue__.$store;
            await store.dispatch('events/fetchEvents');
            const events = store.getters['events/allEvents'];
            
            if (events.length === 0) {
                console.error('No hay eventos disponibles para probar');
                return;
            }
            
            const firstEvent = events[0];
            window.location.href = `/admin/events/${firstEvent.id}`;
            return 'Por favor, ejecuta el test nuevamente después de cargar la página de detalles.';
        }
        
        // 2. Verificar el store de Vuex
        const store = document.querySelector('#app').__vue__.$store;
        const eventDetails = store.state.events.currentEvent;
        
        console.log('Evento actual en el store:', eventDetails);
        
        // 3. Verificar la estructura de la página
        console.log('\n=== Verificando estructura de la página ===');
        
        // Información general del evento
        const eventInfoCard = document.querySelector('.event-detail-card');
        if (eventInfoCard) {
            console.log('✅ Tarjeta de información general encontrada');
            const infoItems = eventInfoCard.querySelectorAll('.event-detail-item');
            console.log(`  - ${infoItems.length} items de información`);
        } else {
            console.error('❌ No se encontró la tarjeta de información general');
        }
        
        // Estadísticas
        const statsCard = document.querySelectorAll('.event-detail-card')[1];
        if (statsCard) {
            console.log('✅ Tarjeta de estadísticas encontrada');
            const stats = statsCard.querySelectorAll('.statistic-card');
            console.log(`  - ${stats.length} estadísticas mostradas`);
            
            stats.forEach((stat, index) => {
                const value = stat.querySelector('.statistic-value')?.textContent;
                const label = stat.querySelector('.statistic-label')?.textContent;
                console.log(`  - ${label}: ${value}`);
            });
        } else {
            console.error('❌ No se encontró la tarjeta de estadísticas');
        }
        
        // Sección de visitantes
        const visitorsSection = document.querySelector('.visitors-section');
        if (visitorsSection) {
            console.log('✅ Sección de visitantes encontrada');
            
            // Verificar si hay visitantes
            const visitorsTable = visitorsSection.querySelector('.visitors-table');
            const emptyState = visitorsSection.querySelector('.empty-state');
            
            if (visitorsTable) {
                const rows = visitorsTable.querySelectorAll('tbody tr');
                console.log(`  - ${rows.length} visitantes en la tabla`);
                
                // Analizar estados de visitantes
                let registrados = 0;
                let checkedIn = 0;
                
                rows.forEach(row => {
                    const status = row.querySelector('.visitor-status');
                    if (status) {
                        if (status.classList.contains('status-checked')) {
                            checkedIn++;
                        } else if (status.classList.contains('status-registered')) {
                            registrados++;
                        }
                    }
                });
                
                console.log(`  - Registrados: ${registrados}`);
                console.log(`  - Con check-in: ${checkedIn}`);
            } else if (emptyState) {
                console.log('  - No hay visitantes registrados para este evento');
            }
        } else {
            console.error('❌ No se encontró la sección de visitantes');
        }
        
        // 4. Verificar funcionalidad de navegación
        console.log('\n=== Verificando navegación ===');
        const backButton = document.querySelector('.btn-back');
        if (backButton) {
            console.log('✅ Botón de volver encontrado');
        } else {
            console.error('❌ No se encontró el botón de volver');
        }
        
        // 5. Verificar acciones disponibles
        console.log('\n=== Verificando acciones ===');
        const editButton = document.querySelector('.event-actions button');
        const exportButton = document.querySelector('.visitors-actions .btn-secondary');
        
        if (editButton) {
            console.log('✅ Botón de editar evento encontrado');
        }
        
        if (exportButton) {
            console.log('✅ Botón de exportar visitantes encontrado');
        }
        
        // 6. Hacer una petición directa al backend para comparar
        console.log('\n=== Verificando datos del backend ===');
        const eventId = window.location.pathname.split('/').pop();
        
        try {
            const response = await fetch(`/api/v1/events/${eventId}`);
            const backendEvent = await response.json();
            console.log('Datos del backend:', backendEvent);
            
            // Comparar conteos
            console.log('\n=== Comparación de conteos ===');
            console.log(`Frontend - Registrados: ${eventDetails?.registeredCount || 0}`);
            console.log(`Backend - Registrados: ${backendEvent.registered_count || 0}`);
            console.log(`Frontend - Check-ins: ${eventDetails?.checkedInCount || 0}`);
            console.log(`Backend - Check-ins: ${backendEvent.checked_in_count || 0}`);
            
        } catch (error) {
            console.error('Error al obtener datos del backend:', error);
        }
        
        // 7. Resumen del test
        console.log('\n=== RESUMEN DEL TEST ===');
        const passed = [];
        const failed = [];
        
        if (eventInfoCard) passed.push('Información del evento');
        else failed.push('Información del evento');
        
        if (statsCard) passed.push('Estadísticas');
        else failed.push('Estadísticas');
        
        if (visitorsSection) passed.push('Sección de visitantes');
        else failed.push('Sección de visitantes');
        
        console.log(`✅ Componentes funcionando: ${passed.join(', ')}`);
        if (failed.length > 0) {
            console.log(`❌ Componentes faltantes: ${failed.join(', ')}`);
        }
        
        if (failed.length === 0) {
            console.log('\n🎉 ¡La vista de detalles está funcionando correctamente!');
        } else {
            console.log('\n⚠️ Algunos componentes no están funcionando correctamente.');
        }
        
    } catch (error) {
        console.error('Error durante el test:', error);
    }
}

// Ejecutar el test
testEventDetailsView();
