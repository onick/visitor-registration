#!/bin/bash

# Script actualizado para abrir el proyecto en el navegador
echo "=== Abriendo Proyecto CCB ==="
echo ""

# Detectar el sistema operativo
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open "http://localhost:8082"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open "http://localhost:8082"
else
    # Windows
    start "http://localhost:8082"
fi

echo "✅ Navegador abierto en: http://localhost:8082"
echo ""
echo "Credenciales de acceso:"
echo "  Usuario: admin"
echo "  Contraseña: Admin123!"
echo ""
echo "Para probar Ver Detalles:"
echo "1. Inicia sesión"
echo "2. Ve a 'Eventos' en el menú lateral"
echo "3. Haz clic en 'Ver Detalles' de cualquier evento"
echo ""
