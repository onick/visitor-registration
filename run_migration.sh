#!/bin/bash

# Script para ejecutar la migración y crear tipos e intereses
echo "=== Ejecutando migración de tipos e intereses ==="

# Cambiar al directorio correcto
cd /Users/marcelinofranciscomartinez/Documents/Projects/ccb01/visitor-registration/backend

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    echo "Activando entorno virtual..."
    source venv/bin/activate
fi

# Ejecutar script de migración
echo "Ejecutando migrations/add_type_interests.py..."
python migrations/add_type_interests.py

echo "=== Migración completada ==="
echo "Ahora el sistema tiene soporte para tipos de eventos e intereses de visitantes"
echo "Puedes acceder al panel de visitantes para ver los intereses calculados"
