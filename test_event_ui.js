// Script de prueba para verificar la gestión de eventos en el frontend
// Ejecutar desde la consola del navegador cuando estés en la aplicación

// Función para verificar la creación de eventos
async function testEventCreation() {
    console.log('=== VERIFICANDO CREACIÓN DE EVENTOS ===');
    
    const store = window.$app?.$store || window.app?.$store;
    if (!store) {
        console.error('No se pudo acceder al store. Asegúrate de estar en la aplicación.');
        return;
    }
    
    // Crear un evento de prueba
    const testEvent = {
        name: `Evento de Prueba ${Date.now()}`,
        description: 'Este es un evento de prueba creado desde la consola',
        startDate: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(), // Mañana
        endDate: new Date(Date.now() + 25 * 60 * 60 * 1000).toISOString(), // Mañana + 1 hora
        location: 'Sala de Pruebas',
        capacity: 100
    };
    
    console.log('Creando evento:', testEvent);
    
    try {
        const result = await store.dispatch('events/createEvent', testEvent);
        console.log('✓ Evento creado exitosamente:', result);
        return result;
    } catch (error) {
        console.error('✗ Error al crear evento:', error);
        return null;
    }
}

// Función para verificar la eliminación de eventos
async function testEventDeletion(eventId) {
    console.log('\n=== VERIFICANDO ELIMINACIÓN DE EVENTOS ===');
    
    const store = window.$app?.$store || window.app?.$store;
    if (!store) {
        console.error('No se pudo acceder al store. Asegúrate de estar en la aplicación.');
        return;
    }
    
    console.log(`Eliminando evento con ID: ${eventId}`);
    
    try {
        await store.dispatch('events/removeEvent', eventId);
        console.log('✓ Evento eliminado exitosamente');
        return true;
    } catch (error) {
        console.error('✗ Error al eliminar evento:', error);
        return false;
    }
}

// Función para listar todos los eventos
async function listEvents() {
    console.log('\n=== LISTANDO EVENTOS ===');
    
    const store = window.$app?.$store || window.app?.$store;
    if (!store) {
        console.error('No se pudo acceder al store. Asegúrate de estar en la aplicación.');
        return;
    }
    
    try {
        await store.dispatch('events/fetchEvents');
        const events = store.getters['events/allEvents'];
        console.log(`Total de eventos: ${events.length}`);
        events.forEach((event, index) => {
            console.log(`${index + 1}. ${event.name || event.title} (ID: ${event.id}, Activo: ${event.isActive || event.is_active})`);
        });
        return events;
    } catch (error) {
        console.error('✗ Error al listar eventos:', error);
        return [];
    }
}

// Función para verificar el modal de creación
function checkCreateModal() {
    console.log('\n=== VERIFICANDO MODAL DE CREACIÓN ===');
    
    // Buscar el botón de crear evento
    const createButton = document.querySelector('button:has(.fa-plus)') || 
                       document.querySelector('[class*="btn-primary"]');
    
    if (createButton) {
        console.log('✓ Botón de crear evento encontrado');
        console.log('  Haciendo clic en el botón...');
        createButton.click();
        
        setTimeout(() => {
            const modal = document.querySelector('.modal-overlay');
            if (modal) {
                console.log('✓ Modal de creación abierto');
                
                // Verificar campos del formulario
                const fields = {
                    name: document.querySelector('#eventName'),
                    startDate: document.querySelector('#eventStartDate'),
                    endDate: document.querySelector('#eventEndDate'),
                    location: document.querySelector('#eventLocation'),
                    description: document.querySelector('#eventDescription'),
                    capacity: document.querySelector('#eventCapacity')
                };
                
                Object.entries(fields).forEach(([key, field]) => {
                    if (field) {
                        console.log(`  ✓ Campo ${key} presente`);
                    } else {
                        console.log(`  ✗ Campo ${key} no encontrado`);
                    }
                });
                
                // Cerrar el modal
                const closeButton = modal.querySelector('.btn-close');
                if (closeButton) {
                    closeButton.click();
                    console.log('  Modal cerrado');
                }
            } else {
                console.log('✗ Modal de creación no encontrado');
            }
        }, 500);
    } else {
        console.log('✗ Botón de crear evento no encontrado');
    }
}

// Función para verificar el botón de eliminar
function checkDeleteButtons() {
    console.log('\n=== VERIFICANDO BOTONES DE ELIMINAR ===');
    
    const deleteButtons = document.querySelectorAll('button:has(.fa-trash), .btn-icon:has(.fa-trash-alt)');
    
    if (deleteButtons.length > 0) {
        console.log(`✓ ${deleteButtons.length} botones de eliminar encontrados`);
        
        // Verificar el primer botón
        const firstButton = deleteButtons[0];
        console.log('  Haciendo clic en el primer botón de eliminar...');
        firstButton.click();
        
        setTimeout(() => {
            const modal = document.querySelector('.delete-modal, .modal-overlay:has(.delete-message)');
            if (modal) {
                console.log('✓ Modal de confirmación de eliminación abierto');
                
                // Buscar botón de cancelar
                const cancelButton = modal.querySelector('.btn-secondary');
                if (cancelButton) {
                    cancelButton.click();
                    console.log('  Modal cerrado (cancelado)');
                }
            } else {
                console.log('✗ Modal de confirmación no encontrado');
            }
        }, 500);
    } else {
        console.log('✗ No se encontraron botones de eliminar');
    }
}

// Ejecutar todas las pruebas
async function runAllTests() {
    console.log('=== INICIANDO PRUEBAS DE GESTIÓN DE EVENTOS ===');
    console.log('Fecha:', new Date().toISOString());
    
    // 1. Listar eventos actuales
    await listEvents();
    
    // 2. Verificar UI
    checkCreateModal();
    
    setTimeout(() => {
        checkDeleteButtons();
    }, 2000);
    
    // 3. Crear un evento de prueba
    setTimeout(async () => {
        const newEvent = await testEventCreation();
        
        if (newEvent) {
            // 4. Listar eventos nuevamente
            await listEvents();
            
            // 5. Eliminar el evento de prueba
            const deleted = await testEventDeletion(newEvent.id);
            
            if (deleted) {
                // 6. Listar eventos finalmente
                await listEvents();
            }
        }
        
        console.log('\n=== PRUEBAS COMPLETADAS ===');
    }, 3000);
}

// Ejecutar pruebas
runAllTests();
