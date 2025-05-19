/**
 * Test para verificar que las tarjetas de eventos muestran los conteos de registrados
 * Este test se ejecuta en el navegador desde la consola del desarrollador
 */

async function testEventCardsWithCounts() {
    console.log('=== Test: Event Cards with Registration Counts ===');
    
    try {
        // 1. Verificar que estamos en la página de eventos
        if (!window.location.pathname.includes('/events') && !window.location.pathname.includes('/admin')) {
            console.log('Navegando a la página de gestión de eventos...');
            window.location.href = '/admin/events';
            return 'Por favor, ejecuta el test nuevamente después de cargar la página de eventos.';
        }
        
        // 2. Verificar el store de Vuex
        const store = document.querySelector('#app').__vue__.$store;
        
        if (!store) {
            throw new Error('No se pudo acceder al store de Vuex');
        }
        
        // 3. Obtener los eventos del store
        const events = store.getters['events/allEvents'];
        console.log('Eventos en el store:', events);
        
        // 4. Verificar que los eventos tienen los campos de conteo
        const eventsWithCounts = events.filter(event => 
            event.registeredCount !== undefined && 
            event.checkedInCount !== undefined
        );
        
        console.log(`${eventsWithCounts.length} de ${events.length} eventos tienen conteos`);
        
        // 5. Verificar las tarjetas en el DOM
        const eventCards = document.querySelectorAll('.event-card');
        console.log(`Tarjetas de eventos encontradas en el DOM: ${eventCards.length}`);
        
        let passedChecks = 0;
        let failedChecks = 0;
        
        eventCards.forEach((card, index) => {
            const statsSection = card.querySelector('.event-stats');
            const registeredStat = card.querySelector('.stat:first-child span');
            const checkedInStat = card.querySelector('.stat:last-child span');
            
            if (statsSection && registeredStat && checkedInStat) {
                const registeredText = registeredStat.textContent;
                const checkedInText = checkedInStat.textContent;
                
                console.log(`Tarjeta ${index + 1}:`);
                console.log(`  - Registrados: ${registeredText}`);
                console.log(`  - Asistentes: ${checkedInText}`);
                
                if (registeredText.includes('registrados') && checkedInText.includes('asistentes')) {
                    passedChecks++;
                } else {
                    failedChecks++;
                    console.error(`  ❌ La tarjeta ${index + 1} no muestra los conteos correctamente`);
                }
            } else {
                failedChecks++;
                console.error(`❌ La tarjeta ${index + 1} no tiene sección de estadísticas`);
            }
        });
        
        // 6. Resultado del test
        console.log('\n=== RESULTADO DEL TEST ===');
        console.log(`✅ Tests pasados: ${passedChecks}`);
        console.log(`❌ Tests fallidos: ${failedChecks}`);
        
        if (failedChecks === 0 && passedChecks > 0) {
            console.log('🎉 ¡Todas las tarjetas muestran los conteos correctamente!');
        } else if (passedChecks === 0) {
            console.log('⚠️ Ninguna tarjeta muestra los conteos. Verifica el backend y el mapeo de datos.');
        } else {
            console.log('⚠️ Algunas tarjetas no muestran los conteos correctamente.');
        }
        
        // 7. Hacer una petición manual al backend para verificar
        console.log('\n=== Verificando respuesta del backend ===');
        const response = await fetch('/api/v1/events/');
        const backendEvents = await response.json();
        
        console.log('Respuesta del backend:', backendEvents);
        
        const backendEventsWithCounts = backendEvents.filter(event => 
            event.registered_count !== undefined && 
            event.checked_in_count !== undefined
        );
        
        if (backendEventsWithCounts.length === 0) {
            console.error('❌ El backend no está devolviendo los conteos. Necesitas actualizar el backend.');
        } else {
            console.log(`✅ El backend devuelve conteos para ${backendEventsWithCounts.length} eventos`);
        }
        
    } catch (error) {
        console.error('Error durante el test:', error);
    }
}

// Ejecutar el test
testEventCardsWithCounts();
