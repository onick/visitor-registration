# Centro Cultural Banreservas - Backend API

API para el sistema de registro de visitantes del Centro Cultural Banreservas.

## Requisitos

- Python 3.9+
- pip

## Instalación

1. Clonar el repositorio:
   ```bash
   git clone <url-repositorio>
   cd visitor-registration/backend
   ```

2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Configuración

Las variables de entorno se pueden configurar en el archivo `run_dev.sh`:

```bash
export FLASK_ENV=development
export USE_SQLITE=true
export ADMIN_EMAIL=admin@ccb.do
export ADMIN_PASSWORD=Admin123!
export FLASK_DEBUG=1
```

## Ejecución del servidor de desarrollo

Para iniciar el servidor de desarrollo con Gunicorn:

```bash
./run_dev.sh
```

El servidor se iniciará en http://0.0.0.0:8080

## Estructura de la API

La API está organizada en los siguientes endpoints principales:

- `/api/v1/auth/` - Autenticación y gestión de usuarios
- `/api/v1/events/` - Gestión de eventos
- `/api/v1/visitors/` - Gestión de visitantes
- `/api/v1/kiosks/` - Gestión de kioscos

## Endpoints principales

### Eventos

- `GET /api/v1/events/` - Obtener lista de eventos
- `GET /api/v1/events/active` - Obtener lista de eventos activos
- `GET /api/v1/events/<id>` - Obtener detalles de un evento
- `POST /api/v1/events/` - Crear un nuevo evento (requiere autenticación)
- `PUT /api/v1/events/<id>` - Actualizar un evento (requiere autenticación)
- `DELETE /api/v1/events/<id>` - Eliminar un evento (requiere autenticación admin)

### Visitantes

- `GET /api/v1/visitors/` - Obtener lista de visitantes (requiere autenticación)
- `GET /api/v1/visitors/<id>` - Obtener detalles de un visitante (requiere autenticación)
- `POST /api/v1/visitors/` - Registrar un nuevo visitante
- `PUT /api/v1/visitors/<id>` - Actualizar información de un visitante (requiere autenticación)
- `DELETE /api/v1/visitors/<id>` - Eliminar un visitante (requiere autenticación admin)

### Kioscos

- `GET /api/v1/kiosks/` - Obtener lista de kioscos (requiere autenticación)
- `GET /api/v1/kiosks/<id>` - Obtener detalles de un kiosco (requiere autenticación)
- `POST /api/v1/kiosks/` - Crear un nuevo kiosco (requiere autenticación admin)
- `PUT /api/v1/kiosks/<id>` - Actualizar un kiosco (requiere autenticación admin)
- `DELETE /api/v1/kiosks/<id>` - Eliminar un kiosco (requiere autenticación admin)

## Autenticación

Para acceder a los endpoints protegidos, se debe incluir un token JWT en el encabezado de la solicitud:

```
Authorization: Bearer <token>
```

Para obtener un token:

```bash
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "Admin123!"}'
```

## Solución de problemas

### Puerto ya en uso

Si al iniciar el servidor aparece el error "Address already in use", ejecute:

```bash
lsof -i :8080  # Para ver qué proceso está usando el puerto
kill -9 <PID>  # Para terminar el proceso
```

### Base de datos

Para reiniciar la base de datos:

```bash
rm dev.db
./run_dev.sh  # La base de datos se recreará automáticamente
```

### Problemas con autenticación JWT

Si recibe errores como "Subject must be a string", la aplicación puede necesitar reiniciarse:

1. Detener el servidor (Ctrl+C)
2. Matar cualquier proceso restante: `lsof -i :8080` y `kill -9 <PID>`
3. Reiniciar el servidor: `./run_dev.sh`

Si sigue teniendo problemas, pruebe a eliminar la base de datos y empezar de nuevo:

```bash
rm dev.db
./run_dev.sh
```

### Documentación de la API

La documentación Swagger de la API está disponible en:

```
http://localhost:8080/api/v1/
```

Para acceder a la interfaz de Swagger, use un navegador en lugar de curl. 