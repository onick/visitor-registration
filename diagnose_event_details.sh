#!/bin/bash

# Script de diagnóstico para Ver Detalles
echo "=== Diagnóstico de Ver Detalles - Proyecto CCB ==="
echo ""

# 1. Verificar que el backend responde
echo "1. Verificando backend..."
EVENTS=$(curl -s http://localhost:8080/api/v1/events/ 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "✅ Backend responde"
    EVENT_COUNT=$(echo $EVENTS | jq '. | length')
    echo "   Eventos encontrados: $EVENT_COUNT"
    
    if [ "$EVENT_COUNT" -gt 0 ]; then
        FIRST_EVENT_ID=$(echo $EVENTS | jq -r '.[0].id')
        FIRST_EVENT_TITLE=$(echo $EVENTS | jq -r '.[0].title')
        echo "   Primer evento: ID=$FIRST_EVENT_ID, Título=$FIRST_EVENT_TITLE"
        
        # 2. Probar endpoint de detalles
        echo ""
        echo "2. Probando endpoint de detalles para evento $FIRST_EVENT_ID..."
        EVENT_DETAILS=$(curl -s http://localhost:8080/api/v1/events/$FIRST_EVENT_ID/ 2>/dev/null)
        if [ $? -eq 0 ]; then
            echo "✅ Endpoint de detalles responde"
            echo "   Datos recibidos:"
            echo $EVENT_DETAILS | jq '.' | head -10
        else
            echo "❌ Error al obtener detalles del evento"
        fi
        
        # 3. Probar endpoint de visitantes
        echo ""
        echo "3. Probando endpoint de visitantes para evento $FIRST_EVENT_ID..."
        VISITORS=$(curl -s http://localhost:8080/api/v1/visitors/event/$FIRST_EVENT_ID 2>/dev/null)
        if [ $? -eq 0 ]; then
            VISITOR_COUNT=$(echo $VISITORS | jq '. | length')
            echo "✅ Endpoint de visitantes responde"
            echo "   Visitantes encontrados: $VISITOR_COUNT"
        else
            echo "❌ Error al obtener visitantes del evento"
        fi
    else
        echo "❌ No hay eventos disponibles para probar"
    fi
else
    echo "❌ Backend no responde. Asegúrate de que esté corriendo en puerto 8080"
fi

# 4. Instrucciones para debug en navegador
echo ""
echo "=== Instrucciones para Debug en Navegador ==="
echo ""
echo "1. Abre Chrome o Firefox"
echo "2. Ve a: http://localhost:8094"
echo "3. Abre la consola del desarrollador (F12)"
echo "4. Ve a la pestaña 'Console'"
echo "5. Inicia sesión como admin"
echo "6. Ve a Eventos y haz clic en 'Ver Detalles'"
echo ""
echo "En la consola deberías ver:"
echo "  - '=== INICIO CARGA DE EVENTO ==='"
echo "  - 'Event ID desde ruta: X'"
echo "  - 'Llamando a fetchEventById...'"
echo "  - 'Respuesta de fetchEventById: ...'"
echo ""
echo "Si ves 'null' o 'undefined' en la respuesta, el problema está en el store de Vuex"
echo ""

# 5. Crear archivo HTML de prueba
cat > test_event_details.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Test Ver Detalles - CCB</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .test { margin: 20px 0; padding: 10px; border: 1px solid #ccc; }
        .success { background-color: #d4edda; }
        .error { background-color: #f8d7da; }
        pre { background-color: #f4f4f4; padding: 10px; }
    </style>
</head>
<body>
    <h1>Test de Ver Detalles - CCB</h1>
    
    <div id="backend-test" class="test">
        <h3>1. Test Backend</h3>
        <div id="backend-result"></div>
    </div>
    
    <div id="event-test" class="test">
        <h3>2. Test Detalles de Evento</h3>
        <div id="event-result"></div>
    </div>
    
    <div id="instructions" class="test">
        <h3>3. Instrucciones para Prueba Manual</h3>
        <ol>
            <li>Abre <a href="http://localhost:8094" target="_blank">http://localhost:8094</a></li>
            <li>Inicia sesión con: admin / Admin123!</li>
            <li>Ve a Eventos</li>
            <li>Haz clic en "Ver Detalles" de cualquier evento</li>
            <li>Observa el cuadro de debug en la parte superior</li>
        </ol>
    </div>

    <script>
        // Test backend
        fetch('http://localhost:8080/api/v1/events/')
            .then(r => r.json())
            .then(events => {
                document.getElementById('backend-result').innerHTML = `
                    <p class="success">✅ Backend funcionando</p>
                    <p>Eventos encontrados: ${events.length}</p>
                `;
                
                if (events.length > 0) {
                    const firstEvent = events[0];
                    return fetch(`http://localhost:8080/api/v1/events/${firstEvent.id}`);
                }
            })
            .then(r => r && r.json())
            .then(eventDetails => {
                if (eventDetails) {
                    document.getElementById('event-result').innerHTML = `
                        <p class="success">✅ Endpoint de detalles funcionando</p>
                        <pre>${JSON.stringify(eventDetails, null, 2)}</pre>
                    `;
                }
            })
            .catch(err => {
                document.getElementById('backend-result').innerHTML = `
                    <p class="error">❌ Error: ${err.message}</p>
                `;
            });
    </script>
</body>
</html>
EOF

echo ""
echo "=== Archivo de prueba creado ==="
echo "Abre test_event_details.html en tu navegador para ver pruebas automáticas"
echo ""
