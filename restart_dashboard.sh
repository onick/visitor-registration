#!/bin/bash

echo "=== Reiniciando el Dashboard CCB ==="
echo ""

# Detener procesos existentes
echo "1. Deteniendo procesos existentes..."
pkill -f "vue-cli-service serve" || true
sleep 2

# Limpiar caché
echo "2. Limpiando caché..."
cd frontend
rm -rf node_modules/.cache

# Reinstalar echarts por si acaso
echo "3. Verificando dependencias..."
npm list echarts || npm install echarts vue-echarts --legacy-peer-deps

# Iniciar el servidor
echo "4. Iniciando servidor frontend..."
npm run serve -- --port 8082 &

# Esperar a que el servidor esté listo
echo "5. Esperando a que el servidor esté listo..."
sleep 5

# Verificar que esté corriendo
echo "6. Verificando servidor..."
curl -s http://localhost:8082 > /dev/null && echo "   ✅ Servidor corriendo en http://localhost:8082" || echo "   ❌ Error al iniciar servidor"

echo ""
echo "Dashboard disponible en:"
echo "  - http://localhost:8082/admin/dashboard"
echo "  - Login: admin / Admin123!"
echo ""
echo "Si sigues viendo errores, revisa la consola del navegador (F12)"
