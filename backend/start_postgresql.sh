#!/bin/bash
# Script para iniciar el backend con PostgreSQL

cd /Users/marcelinofranciscomartinez/Documents/Projects/ccb01/visitor-registration/backend

# Activar entorno virtual
source venv/bin/activate

# Asegurarse de que use PostgreSQL
export FLASK_ENV=production

# Iniciar servidor Flask
python app_production.py
