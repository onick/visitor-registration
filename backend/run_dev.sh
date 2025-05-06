#!/bin/bash

# Configura variables de entorno para desarrollo
export FLASK_ENV=development
export USE_SQLITE=true
export ADMIN_EMAIL=admin@ccb.do
export ADMIN_PASSWORD=Admin123!
export FLASK_DEBUG=1

# Inicializa la base de datos si no existe
if [ ! -f "dev.db" ]; then
    echo "Inicializando base de datos..."
    python utils/init_db.py
fi

# Inicia el servidor con configuración de recarga automática
echo "Iniciando servidor de desarrollo en http://0.0.0.0:8080"
gunicorn -c gunicorn.conf.py wsgi:application 