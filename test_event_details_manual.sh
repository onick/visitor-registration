#!/bin/bash

echo "=== Test de Ver Detalles de Evento ==="
echo ""
echo "Este script verifica que la funcionalidad de Ver Detalles funcione correctamente"
echo ""

# 1. Verificar que el backend esté corriendo
echo "1. Verificando backend..."
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/api/v1/events/)
if [ "$BACKEND_STATUS" -eq 200 ]; then
    echo "✅ Backend está funcionando"
else
    echo "❌ Backend no está funcionando. Inicialo con: cd backend && python app_production.py"
    exit 1
fi

# 2. Verificar que el frontend esté corriendo
echo ""
echo "2. Verificando frontend..."
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8094/)
if [ "$FRONTEND_STATUS" -eq 200 ]; then
    echo "✅ Frontend está funcionando"
else
    echo "❌ Frontend no está funcionando. Inicialo con: cd frontend && npm run serve"
    exit 1
fi

# 3. Obtener el primer evento
echo ""
echo "3. Obteniendo eventos..."
EVENTS=$(curl -s http://localhost:8080/api/v1/events/)
FIRST_EVENT_ID=$(echo $EVENTS | jq -r '.[0].id')
FIRST_EVENT_TITLE=$(echo $EVENTS | jq -r '.[0].title')

if [ "$FIRST_EVENT_ID" != "null" ]; then
    echo "✅ Primer evento encontrado: ID=$FIRST_EVENT_ID, Título=$FIRST_EVENT_TITLE"
else
    echo "❌ No se encontraron eventos"
    exit 1
fi

# 4. Obtener detalles del evento
echo ""
echo "4. Obteniendo detalles del evento $FIRST_EVENT_ID..."
EVENT_DETAILS=$(curl -s http://localhost:8080/api/v1/events/$FIRST_EVENT_ID)
if [ $? -eq 0 ]; then
    echo "✅ Detalles del evento obtenidos:"
    echo $EVENT_DETAILS | jq '.'
else
    echo "❌ Error al obtener detalles del evento"
fi

# 5. Instrucciones para prueba manual
echo ""
echo "=== PRUEBA MANUAL ==="
echo ""
echo "Ahora realiza estos pasos:"
echo ""
echo "1. Abre el navegador en: http://localhost:8094/login"
echo "2. Inicia sesión con: admin / Admin123!"
echo "3. Ve a la sección 'Eventos' del menú"
echo "4. Haz clic en 'Ver Detalles' del primer evento ($FIRST_EVENT_TITLE)"
echo ""
echo "ESPERADO:"
echo "- Deberías ver la información completa del evento"
echo "- En la parte superior verás un cuadro de debug con información"
echo "- Si aparece 'Evento no encontrado', revisa la consola del navegador (F12)"
echo ""
echo "RESULTADO ACTUAL:"
echo "- Si ves el evento correctamente: ✅ La funcionalidad está trabajando"
echo "- Si ves 'Evento no encontrado': ❌ Hay un problema en el store o la acción fetchEventById"
echo ""
echo "Para más debugging, abre la consola del navegador y revisa los logs"
