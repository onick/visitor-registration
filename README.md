# Centro Cultural Banreservas - Plataforma de Gestión de Eventos

Sistema de gestión de eventos para el Centro Cultural Banreservas con sistema de kiosco para auto-registro de visitantes.

## Descripción

Esta plataforma permite al Centro Cultural Banreservas gestionar eventos culturales y facilitar el registro de visitantes a través de kioscos interactivos con pantalla táctil.

## Características Principales

- Gestión de eventos culturales
- Sistema de kiosco con pantalla táctil para auto-registro de visitantes
- Panel administrativo para gestión y reportes
- Estadísticas de asistencia en tiempo real

## Tecnologías

- Backend: Python/Flask (basado en Open Event Server)
- Frontend: Vue.js/React
- Base de datos: PostgreSQL
- Despliegue: Docker

## Estructura del Proyecto

- `/backend`: API y servicios
- `/frontend`: Interfaz web y aplicación para kioscos
- `/docs`: Documentación

## Requisitos

- Docker y Docker Compose
- Git

## Instalación y Ejecución

1. Clonar el repositorio:
   ```
   git clone https://github.com/onick/visitor-registration.git
   cd visitor-registration
   ```

2. Iniciar los servicios con Docker Compose:
   ```
   docker-compose up -d
   ```

3. Acceder a la aplicación:
   - Frontend: http://localhost:8080
   - API Backend: http://localhost:5000/api/v1
   - Documentación API: http://localhost:5000/api/v1/doc
   - Adminer (gestión DB): http://localhost:8081

## Desarrollo

Para trabajar en desarrollo:

1. Backend (Python/Flask):
   ```
   cd backend
   pip install -r requirements.txt
   python app.py
   ```

2. Frontend (Vue.js):
   ```
   cd frontend
   npm install
   npm run serve
   ```

## Endpoints de API

La API proporciona los siguientes endpoints principales:

- `/api/v1/events`: Gestión de eventos
- `/api/v1/visitors`: Gestión de visitantes
- `/api/v1/kiosks`: Gestión de kioscos

## Arquitectura

La aplicación sigue una arquitectura de microservicios:

1. **Backend Flask**: API RESTful para gestión de datos
2. **Frontend Vue.js**: Interfaz de usuario para kioscos y panel administrativo
3. **Base de datos PostgreSQL**: Almacenamiento persistente de datos
4. **Redis**: Caché y broker de mensajes para tareas asíncronas

## Licencia

Este proyecto está licenciado bajo los términos de la licencia MIT.
