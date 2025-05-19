// Script completo para verificar el flujo de confirmación
// Ejecutar en la consola del navegador

console.log('=== VERIFICACIÓN COMPLETA DEL FLUJO DE CONFIRMACIÓN ===');

// 1. Función para simular registro y navegación
async function testConfirmationFlow() {
    const router = window.$app?.$router || window.app?.$router;
    const store = window.$app?.$store || window.app?.$store;
    
    if (!router || !store) {
        console.error('No se puede acceder al router o store');
        return;
    }
    
    console.log('\n1. Simulando datos de registro');
    
    // Obtener un evento activo
    await store.dispatch('events/fetchEvents');
    const events = store.getters['events/allEvents'];
    const activeEvent = events.find(e => e.isActive || e.is_active);
    
    if (!activeEvent) {
        console.error('No hay eventos activos');
        return;
    }
    
    console.log('   Evento seleccionado:', activeEvent.title || activeEvent.name);
    
    // Datos de prueba
    const testData = {
        visitorName: 'Juan Pérez Test',
        eventId: activeEvent.id
    };
    
    console.log('   Datos de prueba:', testData);
    
    // 2. Guardar en localStorage (simular lo que hacen los componentes)
    console.log('\n2. Guardando datos en localStorage');
    localStorage.setItem('lastRegistration', JSON.stringify(testData));
    
    // 3. Navegar a la página de confirmación
    console.log('\n3. Navegando a la página de confirmación');
    await router.push({
        name: 'ConfirmationView',
        params: testData,
        query: testData
    });
    
    // 4. Verificar después de un momento
    setTimeout(() => {
        console.log('\n4. Verificando resultado');
        
        const currentRoute = router.currentRoute.value;
        console.log('   Ruta actual:', currentRoute.name);
        console.log('   Params:', currentRoute.params);
        console.log('   Query:', currentRoute.query);
        
        // Verificar elementos en el DOM
        const confirmationView = document.querySelector('.confirmation-view');
        if (confirmationView) {
            console.log('   ✓ Vista de confirmación cargada');
            
            const infoRows = document.querySelectorAll('.info-row');
            infoRows.forEach(row => {
                const label = row.querySelector('.info-label')?.textContent;
                const value = row.querySelector('.info-value')?.textContent;
                console.log(`   ${label} ${value}`);
            });
            
            // Verificar si hay datos vacíos
            const emptyValues = Array.from(document.querySelectorAll('.info-value'))
                .filter(el => !el.textContent || el.textContent.trim() === '');
            
            if (emptyValues.length > 0) {
                console.warn('\n⚠️  Hay valores vacíos en la confirmación');
                console.log('Esto puede deberse a que el componente no está recuperando correctamente los datos');
            } else {
                console.log('\n✅ Todos los datos se muestran correctamente');
            }
        } else {
            console.error('   ✗ Vista de confirmación no encontrada');
        }
    }, 1500);
}

// 2. Función para verificar el estado actual
function checkCurrentState() {
    console.log('\n=== ESTADO ACTUAL ===');
    
    // Verificar localStorage
    const registrationData = localStorage.getItem('lastRegistration');
    if (registrationData) {
        console.log('Datos en localStorage:', JSON.parse(registrationData));
    } else {
        console.log('No hay datos en localStorage');
    }
    
    // Verificar ruta actual
    const router = window.$app?.$router || window.app?.$router;
    if (router) {
        const currentRoute = router.currentRoute.value;
        console.log('Ruta actual:', currentRoute.path);
        console.log('Params:', currentRoute.params);
        console.log('Query:', currentRoute.query);
    }
    
    // Verificar datos mostrados
    const infoValues = document.querySelectorAll('.info-value');
    if (infoValues.length > 0) {
        console.log('\nDatos mostrados en pantalla:');
        infoValues.forEach((el, index) => {
            const label = el.previousElementSibling?.textContent || `Campo ${index + 1}:`;
            console.log(`   ${label} ${el.textContent}`);
        });
    }
}

// 3. Función para limpiar y reiniciar
function resetConfirmation() {
    console.log('\n=== LIMPIANDO DATOS ===');
    localStorage.removeItem('lastRegistration');
    console.log('Datos de localStorage eliminados');
    
    const router = window.$app?.$router || window.app?.$router;
    if (router) {
        router.push('/kiosk/idle');
        console.log('Navegando a la pantalla de inicio');
    }
}

// Menú de opciones
console.log('\n=== OPCIONES DISPONIBLES ===');
console.log('1. testConfirmationFlow() - Probar flujo completo');
console.log('2. checkCurrentState() - Verificar estado actual');
console.log('3. resetConfirmation() - Limpiar y reiniciar');

// Ejecutar verificación automática
checkCurrentState();
