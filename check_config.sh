#!/bin/bash

echo "=== Verificando configuración del proyecto CCB ==="
echo ""

# Verificar proceso del backend
echo "1. Verificando backend (puerto 8080):"
lsof -i :8080 | grep LISTEN || echo "   ❌ Backend no está corriendo en puerto 8080"
echo ""

# Verificar proceso del frontend
echo "2. Verificando frontend:"
lsof -i :8094 | grep LISTEN && echo "   ✅ Frontend corriendo en puerto 8094"
lsof -i :8082 | grep LISTEN && echo "   ✅ Frontend corriendo en puerto 8082"
echo ""

# Verificar archivos de configuración
echo "3. Configuración del frontend:"
cd frontend
grep -n "port" package.json || echo "   No se encontró configuración de puerto en package.json"
echo ""

echo "4. Rutas disponibles:"
echo "   - Dashboard: http://localhost:[PUERTO]/admin/dashboard"
echo "   - Admin: http://localhost:[PUERTO]/admin"
echo ""

echo "5. Para iniciar los servicios:"
echo "   Backend: cd backend && python app.py"
echo "   Frontend: cd frontend && npm run serve"
echo ""

# Verificar si hay un archivo de configuración de puerto específico
if [ -f ".env" ]; then
    echo "6. Variables de entorno (.env):"
    grep PORT .env
elif [ -f "frontend/.env" ]; then
    echo "6. Variables de entorno (frontend/.env):"
    grep PORT frontend/.env
fi
