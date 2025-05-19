#!/bin/bash

# Script para iniciar el proyecto CCB
echo "🚀 Iniciando proyecto CCB - Centro Cultural Banreservas"
echo "=================================================="

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Directorio base del proyecto
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

# Función para verificar si un puerto está en uso
check_port() {
    lsof -ti:$1 > /dev/null
    return $?
}

# Función para matar procesos en un puerto
kill_port() {
    if check_port $1; then
        echo -e "${YELLOW}Puerto $1 en uso. Deteniendo proceso...${NC}"
        lsof -ti:$1 | xargs kill -9
        sleep 1
    fi
}

# Iniciar backend
start_backend() {
    echo -e "\n${GREEN}1. Iniciando Backend...${NC}"
    cd $BACKEND_DIR
    
    # Verificar si existe el entorno virtual
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}Creando entorno virtual...${NC}"
        python3 -m venv venv
    fi
    
    # Activar entorno virtual e instalar dependencias
    source venv/bin/activate
    
    # Verificar si requirements.txt existe
    if [ -f "requirements.txt" ]; then
        echo -e "${YELLOW}Instalando dependencias del backend...${NC}"
        pip install -r requirements.txt > /dev/null 2>&1
    fi
    
    # Matar procesos existentes en el puerto 8080
    kill_port 8080
    
    # Iniciar backend
    echo -e "${GREEN}Iniciando servidor Flask en puerto 8080...${NC}"
    python app.py &
    BACKEND_PID=$!
    echo "Backend PID: $BACKEND_PID"
    
    # Esperar a que el backend esté listo
    echo -e "${YELLOW}Esperando a que el backend esté listo...${NC}"
    sleep 3
    
    # Verificar si el backend está respondiendo
    if curl -s http://localhost:8080/api/v1/events/ > /dev/null; then
        echo -e "${GREEN}✓ Backend iniciado correctamente${NC}"
    else
        echo -e "${RED}✗ Error al iniciar el backend${NC}"
        exit 1
    fi
}

# Iniciar frontend
start_frontend() {
    echo -e "\n${GREEN}2. Iniciando Frontend...${NC}"
    cd $FRONTEND_DIR
    
    # Verificar si node_modules existe
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}Instalando dependencias del frontend...${NC}"
        npm install
    fi
    
    # Matar procesos existentes en el puerto 8094
    kill_port 8094
    
    # Iniciar frontend
    echo -e "${GREEN}Iniciando servidor Vue.js en puerto 8094...${NC}"
    npm run serve -- --port 8094 &
    FRONTEND_PID=$!
    echo "Frontend PID: $FRONTEND_PID"
    
    # Esperar a que el frontend esté listo
    echo -e "${YELLOW}Esperando a que el frontend esté listo...${NC}"
    sleep 5
    
    echo -e "${GREEN}✓ Frontend iniciado correctamente${NC}"
}

# Mostrar información de acceso
show_info() {
    echo -e "\n${GREEN}=================================================="
    echo "PROYECTO CCB INICIADO EXITOSAMENTE"
    echo "=================================================="
    echo -e "Backend API: ${YELLOW}http://localhost:8080/api/v1${NC}"
    echo -e "Frontend:    ${YELLOW}http://localhost:8094${NC}"
    echo -e "\nEndpoints disponibles:"
    echo "  - GET  /api/v1/events/"
    echo "  - POST /api/v1/visitors/register" 
    echo "  - GET  /api/v1/visitors/statistics"
    echo -e "\nPresiona ${RED}Ctrl+C${NC} para detener ambos servidores"
    echo -e "==================================================${NC}\n"
}

# Función para limpiar al salir
cleanup() {
    echo -e "\n${YELLOW}Deteniendo servidores...${NC}"
    
    # Detener backend
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo -e "${GREEN}✓ Backend detenido${NC}"
    fi
    
    # Detener frontend
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo -e "${GREEN}✓ Frontend detenido${NC}"
    fi
    
    # Limpiar otros procesos que puedan quedar
    kill_port 8080
    kill_port 8094
    
    echo -e "${GREEN}Proyecto detenido correctamente${NC}"
    exit 0
}

# Capturar señal de interrupción
trap cleanup INT

# Menú principal
case "${1:-all}" in
    backend)
        start_backend
        show_info
        wait $BACKEND_PID
        ;;
    frontend)
        start_frontend
        show_info
        wait $FRONTEND_PID
        ;;
    all)
        start_backend
        start_frontend
        show_info
        wait $BACKEND_PID $FRONTEND_PID
        ;;
    *)
        echo "Uso: $0 [backend|frontend|all]"
        echo "  backend  - Inicia solo el backend"
        echo "  frontend - Inicia solo el frontend"
        echo "  all      - Inicia backend y frontend (predeterminado)"
        exit 1
        ;;
esac
