# Migración a PostgreSQL para el proyecto CCB

## ¿Por qué migrar a PostgreSQL?

Con el volumen esperado de 200+ visitantes diarios, SQLite no es adecuado por:
- Limitaciones de concurrencia (solo un proceso de escritura)
- Riesgo de corrupción con múltiples escrituras simultáneas
- Rendimiento degradado con alto volumen de datos
- Sin soporte para conexiones concurrentes

## Ventajas de PostgreSQL

1. **Concurrencia real**: Múltiples usuarios/kioscos pueden registrar simultáneamente
2. **Escalabilidad**: Maneja millones de registros sin degradación
3. **Integridad de datos**: ACID compliant, transacciones robustas
4. **Rendimiento**: Optimizaciones avanzadas, índices eficientes
5. **Respaldos en caliente**: Backup sin detener el servicio

## Pasos para la migración

### 1. Instalar PostgreSQL

En Ubuntu/Debian:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

En macOS:
```bash
brew install postgresql
brew services start postgresql
```

### 2. Crear base de datos y usuario

```sql
sudo -u postgres psql

-- Crear usuario
CREATE USER ccb_user WITH PASSWORD 'ccb_password_seguro';

-- Crear base de datos
CREATE DATABASE ccb_production;

-- Dar permisos
GRANT ALL PRIVILEGES ON DATABASE ccb_production TO ccb_user;

-- Salir
\q
```

### 3. Instalar psycopg2

```bash
cd backend
source venv/bin/activate
pip install psycopg2-binary flask-migrate
```

### 4. Configurar variables de entorno

Crear archivo `.env`:
```env
FLASK_ENV=production
DATABASE_URL=postgresql://ccb_user:ccb_password_seguro@localhost:5432/ccb_production
SECRET_KEY=tu-clave-secreta-muy-segura
```

### 5. Inicializar migraciones

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 6. Migrar datos existentes

Script para migrar datos de SQLite a PostgreSQL:

```python
# migrate_data.py
import sqlite3
from datetime import datetime
from app_production import app, db
from models.visitor import Visitor, VisitorCheckIn
from models.event import Event
from models.user import User
from models.kiosk import Kiosk

def migrate_data():
    """Migrar datos de SQLite a PostgreSQL"""
    
    # Conectar a SQLite
    sqlite_conn = sqlite3.connect('app.db')
    sqlite_conn.row_factory = sqlite3.Row
    cursor = sqlite_conn.cursor()
    
    with app.app_context():
        # Migrar kioscos
        cursor.execute("SELECT * FROM kiosks")
        for row in cursor.fetchall():
            kiosk = Kiosk(
                id=row['id'],
                name=row['name'],
                location=row['location'],
                is_active=row['is_active']
            )
            db.session.add(kiosk)
        
        # Migrar usuarios
        cursor.execute("SELECT * FROM users")
        for row in cursor.fetchall():
            user = User(
                id=row['id'],
                username=row['username'],
                email=row['email'],
                password_hash=row['password_hash']
            )
            db.session.add(user)
        
        # Migrar eventos
        cursor.execute("SELECT * FROM events")
        for row in cursor.fetchall():
            event = Event(
                id=row['id'],
                title=row['title'],
                description=row['description'],
                start_date=datetime.fromisoformat(row['start_date']),
                end_date=datetime.fromisoformat(row['end_date']),
                location=row['location'],
                is_active=row['is_active']
            )
            db.session.add(event)
        
        # Migrar visitantes
        cursor.execute("SELECT * FROM visitors")
        for row in cursor.fetchall():
            visitor = Visitor(
                id=row['id'],
                name=row['name'],
                email=row['email'],
                phone=row['phone'],
                registration_code=row['registration_code']
            )
            db.session.add(visitor)
        
        # Migrar check-ins
        cursor.execute("SELECT * FROM visitor_check_ins")
        for row in cursor.fetchall():
            checkin = VisitorCheckIn(
                id=row['id'],
                visitor_id=row['visitor_id'],
                event_id=row['event_id'],
                kiosk_id=row['kiosk_id'],
                check_in_time=datetime.fromisoformat(row['check_in_time'])
            )
            db.session.add(checkin)
        
        # Commit todos los datos
        db.session.commit()
        print("Migración completada exitosamente")
    
    sqlite_conn.close()

if __name__ == "__main__":
    migrate_data()
```

### 7. Optimizaciones para alto volumen

Agregar índices para mejorar rendimiento:

```python
# models/visitor.py
class Visitor(db.Model):
    __tablename__ = 'visitors'
    __table_args__ = (
        db.Index('idx_visitor_email', 'email'),
        db.Index('idx_visitor_code', 'registration_code'),
        db.Index('idx_visitor_created', 'created_at'),
    )
    # ... resto del modelo
```

### 8. Configuración de backup automático

Script para backup diario:

```bash
#!/bin/bash
# backup_db.sh

BACKUP_DIR="/var/backups/ccb"
DB_NAME="ccb_production"
DB_USER="ccb_user"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

pg_dump -U $DB_USER -d $DB_NAME > $BACKUP_DIR/ccb_backup_$DATE.sql

# Mantener solo últimos 7 días
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
```

Configurar en crontab:
```bash
0 2 * * * /path/to/backup_db.sh
```

### 9. Monitoreo de rendimiento

Instalar pg_stat_statements:

```sql
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
```

Ver consultas lentas:
```sql
SELECT query, 
       calls, 
       mean::integer as avg_ms, 
       total_time::integer as total_ms
FROM pg_stat_statements
WHERE mean > 100
ORDER BY mean DESC
LIMIT 10;
```

### 10. Configuración de producción

Actualizar `requirements.txt`:
```
Flask==2.3.2
Flask-SQLAlchemy==3.0.5
Flask-CORS==4.0.0
Flask-Migrate==4.0.4
psycopg2-binary==2.9.7
gunicorn==21.2.0
```

Archivo de configuración Gunicorn:
```python
# gunicorn.conf.py
bind = "0.0.0.0:8080"
workers = 4
worker_class = "sync"
worker_connections = 1000
keepalive = 5
```

Ejecutar en producción:
```bash
gunicorn -c gunicorn.conf.py app_production:app
```

## Consideraciones de seguridad

1. **Conexiones SSL**: Habilitar SSL para conexiones a la BD
2. **Firewall**: Restringir acceso al puerto 5432
3. **Passwords seguros**: Usar passwords complejos
4. **Backups encriptados**: Encriptar archivos de backup
5. **Acceso restringido**: Solo permitir conexiones desde servidores autorizados

## Pruebas de carga

Script para probar concurrencia:
```python
# test_load.py
import concurrent.futures
import requests
import time

def register_visitor(i):
    data = {
        "name": f"Test User {i}",
        "email": f"test{i}@example.com",
        "event_id": 1
    }
    response = requests.post(
        "http://localhost:8080/api/v1/visitors/register",
        json=data
    )
    return response.status_code

def load_test(num_requests=200):
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(register_visitor, i) for i in range(num_requests)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    
    end_time = time.time()
    successful = sum(1 for r in results if r == 201)
    
    print(f"Completado: {num_requests} solicitudes en {end_time - start_time:.2f} segundos")
    print(f"Exitosas: {successful}")
    print(f"Fallidas: {num_requests - successful}")

if __name__ == "__main__":
    load_test(200)
```

## Checklist de migración

- [ ] PostgreSQL instalado y configurado
- [ ] Base de datos y usuario creados
- [ ] Dependencias Python instaladas
- [ ] Variables de entorno configuradas
- [ ] Esquema de base de datos migrado
- [ ] Datos existentes migrados
- [ ] Índices creados
- [ ] Backups configurados
- [ ] Pruebas de carga realizadas
- [ ] Aplicación funcionando en producción

## Comandos útiles

```bash
# Verificar conexión a PostgreSQL
psql -U ccb_user -d ccb_production -c "SELECT 1;"

# Ver tamaño de base de datos
psql -U ccb_user -d ccb_production -c "SELECT pg_database_size('ccb_production');"

# Ver número de conexiones activas
psql -U ccb_user -d ccb_production -c "SELECT count(*) FROM pg_stat_activity;"

# Reiniciar secuencias después de migración
psql -U ccb_user -d ccb_production -c "SELECT setval('visitors_id_seq', (SELECT MAX(id) FROM visitors));"
```
