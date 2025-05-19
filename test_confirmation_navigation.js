// Script para probar la navegación a la página de confirmación
// Ejecutar desde la consola del navegador

console.log('=== PRUEBA DE NAVEGACIÓN A CONFIRMACIÓN ===');

// 1. Verificar router
const router = window.$app?.$router || window.app?.$router;
if (!router) {
    console.error('No se pudo acceder al router');
} else {
    console.log('✓ Router disponible');
    
    // 2. Simular navegación a confirmación con datos de prueba
    console.log('\n2. Probando navegación a confirmación:');
    
    const testData = {
        name: 'ConfirmationView',
        params: {
            eventId: 1,
            visitorName: 'Juan Pérez Test'
        }
    };
    
    console.log('Navegando con datos:', testData);
    
    try {
        router.push(testData);
        console.log('✓ Navegación iniciada');
        
        // Verificar después de un momento
        setTimeout(() => {
            const currentRoute = router.currentRoute.value;
            console.log('\n3. Ruta actual:');
            console.log('   Nombre:', currentRoute.name);
            console.log('   Params:', currentRoute.params);
            console.log('   Query:', currentRoute.query);
            
            // Verificar componente actual
            const confirmationComponent = document.querySelector('.confirmation-view');
            if (confirmationComponent) {
                console.log('\n✓ Componente de confirmación cargado');
                
                // Verificar datos mostrados
                const visitorName = document.querySelector('.info-value')?.textContent;
                const eventName = document.querySelectorAll('.info-value')[1]?.textContent;
                const code = document.querySelector('.confirmation-code')?.textContent;
                
                console.log('\n4. Datos mostrados:');
                console.log('   Nombre:', visitorName || 'NO ENCONTRADO');
                console.log('   Evento:', eventName || 'NO ENCONTRADO');
                console.log('   Código:', code || 'NO ENCONTRADO');
                
                if (!visitorName || !eventName) {
                    console.warn('\n⚠️  Los datos no se están mostrando correctamente');
                    console.log('Esto puede deberse a que los parámetros no se están pasando correctamente');
                }
            } else {
                console.error('✗ Componente de confirmación no encontrado');
            }
        }, 1000);
    } catch (error) {
        console.error('Error al navegar:', error);
    }
}

// 4. Función para probar navegación manual
console.log('\n5. Para probar navegación manual:');
console.log('   router.push({');
console.log('     name: "ConfirmationView",');
console.log('     params: {');
console.log('       eventId: 1,');
console.log('       visitorName: "Nombre de Prueba"');
console.log('     }');
console.log('   })');
