#!/bin/bash

# Script para iniciar el proyecto CCB completo
echo "=== Iniciando Proyecto CCB - Sistema de Registro de Visitantes ==="
echo ""

# Colores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar si estamos en el directorio correcto
if [ ! -f "start_project.sh" ]; then
    echo -e "${RED}Error: No estás en el directorio correcto del proyecto${NC}"
    echo "Por favor, ejecuta este script desde: /Users/marcelinofranciscomartinez/Documents/Projects/ccb01/visitor-registration"
    exit 1
fi

# Función para matar procesos en un puerto específico
kill_port() {
    local port=$1
    echo -e "${YELLOW}Verificando puerto $port...${NC}"
    lsof -ti:$port | xargs kill -9 2>/dev/null || true
}

# Limpiar puertos
echo -e "${YELLOW}Limpiando puertos anteriores...${NC}"
kill_port 8080
kill_port 8081
sleep 2

# 1. Iniciar Backend
echo -e "\n${GREEN}1. Iniciando Backend (PostgreSQL)...${NC}"
cd backend

# Verificar si existe el entorno virtual
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creando entorno virtual...${NC}"
    python3 -m venv venv
fi

# Activar entorno virtual e instalar dependencias
source venv/bin/activate
pip install -r requirements.txt -q

# Iniciar backend en background
echo -e "${GREEN}Iniciando backend en puerto 8080...${NC}"
FLASK_ENV=production python app_production.py > backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Esperar a que el backend esté listo
echo -e "${YELLOW}Esperando a que el backend esté listo...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:8080/api/v1/events/ > /dev/null; then
        echo -e "${GREEN}✓ Backend está listo${NC}"
        break
    fi
    echo -n "."
    sleep 1
done

# 2. Iniciar Frontend
echo -e "\n${GREEN}2. Iniciando Frontend...${NC}"
cd ../frontend

# Instalar dependencias si es necesario
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Instalando dependencias del frontend...${NC}"
    npm install
fi

# Iniciar frontend en background
echo -e "${GREEN}Iniciando frontend en puerto 8081...${NC}"
npm run serve > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

# Esperar a que el frontend esté listo
echo -e "${YELLOW}Esperando a que el frontend esté listo...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:8081 > /dev/null; then
        echo -e "${GREEN}✓ Frontend está listo${NC}"
        break
    fi
    echo -n "."
    sleep 1
done

cd ..

# 3. Mostrar información útil
echo -e "\n${GREEN}=== Proyecto CCB Iniciado Exitosamente ===${NC}"
echo ""
echo -e "${GREEN}URLs disponibles:${NC}"
echo -e "  Frontend: ${YELLOW}http://localhost:8081${NC}"
echo -e "  Backend API: ${YELLOW}http://localhost:8080/api/v1${NC}"
echo ""
echo -e "${GREEN}Credenciales de administrador:${NC}"
echo -e "  Usuario: ${YELLOW}admin${NC}"
echo -e "  Contraseña: ${YELLOW}Admin123!${NC}"
echo ""
echo -e "${GREEN}Para ver los logs:${NC}"
echo -e "  Backend: ${YELLOW}tail -f backend/backend.log${NC}"
echo -e "  Frontend: ${YELLOW}tail -f frontend/frontend.log${NC}"
echo ""
echo -e "${GREEN}Para detener el proyecto:${NC}"
echo -e "  ${YELLOW}kill $BACKEND_PID $FRONTEND_PID${NC}"
echo -e "  O presiona Ctrl+C"
echo ""
echo -e "${GREEN}=== Instrucciones para probar Ver Detalles ===${NC}"
echo ""
echo "1. Abre el navegador en: http://localhost:8081"
echo "2. Inicia sesión con las credenciales de arriba"
echo "3. Ve a 'Eventos' en el menú lateral"
echo "4. Haz clic en 'Ver Detalles' de cualquier evento"
echo ""
echo -e "${YELLOW}NOTA: Si ves 'Evento no encontrado', revisa la consola del navegador (F12)${NC}"
echo -e "${YELLOW}      Verás un cuadro de debug en la parte superior con información útil${NC}"
echo ""

# Guardar PIDs para poder detener los procesos después
echo "$BACKEND_PID" > .backend.pid
echo "$FRONTEND_PID" > .frontend.pid

# Crear script para detener el proyecto
cat > stop_project.sh << 'EOF'
#!/bin/bash
echo "Deteniendo proyecto CCB..."
if [ -f .backend.pid ]; then
    kill $(cat .backend.pid) 2>/dev/null || true
    rm .backend.pid
fi
if [ -f .frontend.pid ]; then
    kill $(cat .frontend.pid) 2>/dev/null || true
    rm .frontend.pid
fi
echo "Proyecto detenido"
EOF
chmod +x stop_project.sh

echo -e "${GREEN}Script para detener el proyecto creado: ${YELLOW}./stop_project.sh${NC}"
echo ""
echo -e "${GREEN}Presiona Ctrl+C para detener ambos servicios${NC}"

# Mantener el script ejecutándose
trap "kill $BACKEND_PID $FRONTEND_PID; rm -f .backend.pid .frontend.pid; exit" INT
wait
