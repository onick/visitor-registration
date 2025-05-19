/**
 * Test para verificar el sistema de check-in con código de registro
 * Este test se ejecuta en el navegador desde la consola del desarrollador
 */

async function testQuickCheckIn() {
    console.log('=== Test: Sistema de Check-in Rápido ===');
    
    try {
        // 1. Verificar que estamos en la página de check-in
        if (!window.location.pathname.includes('/kiosk/checkin')) {
            console.log('Navegando a la página de check-in...');
            window.location.href = '/kiosk/checkin';
            return 'Por favor, ejecuta el test nuevamente después de cargar la página de check-in.';
        }
        
        // 2. Simular ingreso de código
        console.log('\n=== Probando diferentes tipos de códigos ===');
        
        // Test con ID numérico
        await testCodeVerification('1', 'ID numérico');
        
        // Test con email
        await testCodeVerification('juan.perez@ejemplo.com', 'Email');
        
        // Test con código inválido
        await testCodeVerification('INVALID-CODE', 'Código inválido');
        
        // 3. Verificar la interfaz
        console.log('\n=== Verificando elementos de la interfaz ===');
        checkUIElements();
        
        // 4. Probar flujo completo
        console.log('\n=== Probando flujo completo de check-in ===');
        await testCompleteFlow();
        
    } catch (error) {
        console.error('Error durante el test:', error);
    }
}

async function testCodeVerification(code, type) {
    console.log(`\nProbando con ${type}: ${code}`);
    
    try {
        const response = await fetch('/api/v1/visitors/verify-code', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ code })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            console.log(`✅ Código válido - Visitante: ${data.visitor.name}`);
            console.log(`   Eventos disponibles: ${data.events.length}`);
            
            data.events.forEach(event => {
                console.log(`   - ${event.title} (${event.checked_in ? 'Ya registrado' : 'Pendiente'})`);
            });
        } else {
            console.log(`❌ Error: ${data.error}`);
        }
        
        return { success: response.ok, data };
        
    } catch (error) {
        console.error(`❌ Error al verificar código: ${error.message}`);
        return { success: false, error };
    }
}

function checkUIElements() {
    const elements = {
        'Scanner QR': '.qr-scanner-container',
        'Botón ingresar código': '.btn-secondary',
        'Campo de código': '#confirmation-code',
        'Botón verificar': '.btn-primary'
    };
    
    Object.entries(elements).forEach(([name, selector]) => {
        const element = document.querySelector(selector);
        if (element) {
            console.log(`✅ ${name} encontrado`);
        } else {
            console.log(`❌ ${name} no encontrado`);
        }
    });
}

async function testCompleteFlow() {
    // Simular clic en "Ingresar código manualmente"
    const manualButton = document.querySelector('.alternative-options .btn-secondary');
    if (manualButton) {
        console.log('1. Cambiando a entrada manual...');
        manualButton.click();
        
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Ingresar código
        const codeInput = document.querySelector('#confirmation-code');
        if (codeInput) {
            console.log('2. Ingresando código de prueba...');
            codeInput.value = '1';
            
            // Simular evento de input
            const inputEvent = new Event('input', { bubbles: true });
            codeInput.dispatchEvent(inputEvent);
            
            await new Promise(resolve => setTimeout(resolve, 500));
            
            // Verificar código
            const verifyButton = document.querySelector('.action-buttons .btn-primary');
            if (verifyButton && !verifyButton.disabled) {
                console.log('3. Verificando código...');
                verifyButton.click();
                
                await new Promise(resolve => setTimeout(resolve, 2000));
                
                // Verificar que se muestre la lista de eventos o el mensaje de éxito
                const eventsSection = document.querySelector('.events-section');
                const successSection = document.querySelector('.success-section');
                
                if (eventsSection) {
                    console.log('✅ Lista de eventos mostrada correctamente');
                    
                    // Intentar hacer check-in en el primer evento
                    const checkInButton = document.querySelector('.event-card:not(.checked-in) .btn-primary');
                    if (checkInButton) {
                        console.log('4. Haciendo check-in...');
                        checkInButton.click();
                        
                        await new Promise(resolve => setTimeout(resolve, 2000));
                        
                        if (document.querySelector('.success-section')) {
                            console.log('✅ Check-in completado exitosamente');
                        }
                    }
                } else if (successSection) {
                    console.log('✅ Check-in directo completado exitosamente');
                } else {
                    console.log('❌ No se encontró la sección esperada');
                }
            }
        }
    }
}

// Ejecutar el test
testQuickCheckIn();
