#!/bin/bash

# Script de instalación para PostgreSQL y migración

## Este script instala PostgreSQL y prepara la base de datos para el proyecto CCB

# Colores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Instalación de PostgreSQL para CCB ===${NC}\n"

# Detectar sistema operativo
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
else
    echo -e "${RED}Sistema operativo no soportado${NC}"
    exit 1
fi

# Instalar PostgreSQL
echo -e "${YELLOW}Instalando PostgreSQL...${NC}"
if [[ "$OS" == "macos" ]]; then
    if ! command -v brew &> /dev/null; then
        echo -e "${RED}Homebrew no está instalado. Por favor instálalo primero.${NC}"
        exit 1
    fi
    brew install postgresql
    brew services start postgresql
else
    sudo apt update
    sudo apt install -y postgresql postgresql-contrib
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
fi

# Crear usuario y base de datos
echo -e "\n${YELLOW}Configurando base de datos...${NC}"

# Generar contraseña segura
DB_PASSWORD=$(openssl rand -base64 12)
DB_USER="ccb_user"
DB_NAME="ccb_production"

# Crear script SQL temporal
cat > /tmp/setup_ccb_db.sql << EOF
-- Crear usuario
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';

-- Crear base de datos
CREATE DATABASE $DB_NAME OWNER $DB_USER;

-- Dar permisos
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;

-- Crear base de datos de desarrollo también
CREATE DATABASE ccb_development OWNER $DB_USER;
GRANT ALL PRIVILEGES ON DATABASE ccb_development TO $DB_USER;
EOF

# Ejecutar script SQL
if [[ "$OS" == "macos" ]]; then
    psql -U $USER -f /tmp/setup_ccb_db.sql
else
    sudo -u postgres psql -f /tmp/setup_ccb_db.sql
fi

# Limpiar
rm /tmp/setup_ccb_db.sql

# Crear archivo .env
echo -e "\n${YELLOW}Creando archivo de configuración...${NC}"
cd backend

cat > .env << EOF
# Configuración de base de datos
FLASK_ENV=production
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME
SECRET_KEY=$(openssl rand -base64 32)

# URLs de desarrollo
DEVELOPMENT_DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/ccb_development

# Configuración de email (actualizar con valores reales)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-app-password
EOF

echo -e "${GREEN}✓ Archivo .env creado${NC}"

# Instalar dependencias Python
echo -e "\n${YELLOW}Instalando dependencias Python...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install psycopg2-binary flask-migrate

# Crear nuevo requirements.txt con PostgreSQL
cat > requirements_postgresql.txt << EOF
Flask==2.3.2
Flask-SQLAlchemy==3.0.5
Flask-CORS==4.0.0
Flask-Migrate==4.0.4
Flask-Mail==0.9.1
psycopg2-binary==2.9.7
gunicorn==21.2.0
python-dotenv==1.0.0
EOF

echo -e "${GREEN}✓ Dependencias instaladas${NC}"

# Inicializar base de datos
echo -e "\n${YELLOW}Inicializando base de datos...${NC}"

# Crear directorio de migraciones si no existe
if [ ! -d "migrations" ]; then
    export FLASK_APP=app_production.py
    flask db init
fi

# Ejecutar migraciones
flask db migrate -m "Initial migration for PostgreSQL"
flask db upgrade

echo -e "${GREEN}✓ Base de datos inicializada${NC}"

# Copiar y actualizar el archivo principal de la aplicación
echo -e "\n${YELLOW}Actualizando aplicación para PostgreSQL...${NC}"
cp app.py app_sqlite_backup.py
cp app_production.py app.py

echo -e "${GREEN}✓ Aplicación actualizada${NC}"

# Migrar datos existentes (si existen)
if [ -f "app.db" ]; then
    echo -e "\n${YELLOW}Migrando datos existentes...${NC}"
    python migrate_to_postgresql.py
    echo -e "${GREEN}✓ Datos migrados${NC}"
fi

# Crear script de inicio para producción
cat > start_production.sh << 'EOF'
#!/bin/bash

# Activar entorno virtual
source venv/bin/activate

# Cargar variables de entorno
export $(cat .env | xargs)

# Iniciar con Gunicorn
gunicorn -c gunicorn.conf.py app:app
EOF

chmod +x start_production.sh

# Crear servicio systemd (solo Linux)
if [[ "$OS" == "linux" ]]; then
    echo -e "\n${YELLOW}Creando servicio systemd...${NC}"
    
    sudo cat > /etc/systemd/system/ccb-backend.service << EOF
[Unit]
Description=CCB Backend Service
After=network.target postgresql.service

[Service]
Type=notify
User=$USER
WorkingDirectory=$(pwd)
Environment="PATH=$(pwd)/venv/bin"
ExecStart=$(pwd)/venv/bin/gunicorn -c gunicorn.conf.py app:app
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    echo -e "${GREEN}✓ Servicio systemd creado${NC}"
    echo -e "Para iniciar el servicio: ${YELLOW}sudo systemctl start ccb-backend${NC}"
fi

# Crear script de backup
cat > backup_database.sh << 'EOF'
#!/bin/bash

# Script de backup para base de datos CCB

BACKUP_DIR="/var/backups/ccb"
DB_NAME="ccb_production"
DB_USER="ccb_user"
DATE=$(date +%Y%m%d_%H%M%S)

# Crear directorio si no existe
mkdir -p $BACKUP_DIR

# Leer password del archivo .env
source .env
DB_PASSWORD=$(echo $DATABASE_URL | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p')

# Hacer backup
PGPASSWORD=$DB_PASSWORD pg_dump -U $DB_USER -h localhost $DB_NAME > $BACKUP_DIR/ccb_backup_$DATE.sql

# Comprimir
gzip $BACKUP_DIR/ccb_backup_$DATE.sql

# Mantener solo últimos 7 días
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "Backup completado: $BACKUP_DIR/ccb_backup_$DATE.sql.gz"
EOF

chmod +x backup_database.sh

# Resumen final
echo -e "\n${GREEN}=== Instalación Completada ===${NC}"
echo -e "\nInformación de la base de datos:"
echo -e "  Usuario: ${YELLOW}$DB_USER${NC}"
echo -e "  Base de datos: ${YELLOW}$DB_NAME${NC}"
echo -e "  Password: ${YELLOW}$DB_PASSWORD${NC}"
echo -e "\nLa configuración se ha guardado en: ${YELLOW}backend/.env${NC}"
echo -e "\nPara iniciar el servidor:"
echo -e "  Desarrollo: ${YELLOW}cd backend && source venv/bin/activate && python app.py${NC}"
echo -e "  Producción: ${YELLOW}cd backend && ./start_production.sh${NC}"

if [[ "$OS" == "linux" ]]; then
    echo -e "\nServicio systemd:"
    echo -e "  Iniciar: ${YELLOW}sudo systemctl start ccb-backend${NC}"
    echo -e "  Detener: ${YELLOW}sudo systemctl stop ccb-backend${NC}"
    echo -e "  Estado: ${YELLOW}sudo systemctl status ccb-backend${NC}"
fi

echo -e "\nScript de backup: ${YELLOW}backend/backup_database.sh${NC}"
echo -e "\n${GREEN}¡PostgreSQL está listo para manejar 200+ visitantes diarios!${NC}"
