# Plataforma CCB - Centro Cultural Banreservas

## 📋 Descripción
Sistema web para la gestión de eventos culturales y registro de visitantes del Centro Cultural Banreservas.

## 🚀 Características principales
- Gestión completa de eventos culturales
- Registro de visitantes con check-in
- Panel administrativo con estadísticas
- Kioscos de autoregistro
- API RESTful
- Interfaz responsive

## 🛠️ Tecnologías utilizadas

### Backend
- Python 3.x
- Flask (Framework web)
- SQLAlchemy (ORM)
- SQLite (Base de datos - desarrollo)
- Flask-CORS (Manejo de CORS)

### Frontend
- Vue.js 3
- Vuex (Gestión de estado)
- Vue Router
- Axios (Cliente HTTP)
- JavaScript ES6+
- HTML5/CSS3

## 📁 Estructura del proyecto

```
visitor-registration/
├── backend/
│   ├── models/         # Modelos de base de datos
│   ├── controllers/    # Controladores
│   ├── services/       # Lógica de negocio
│   ├── api/           # Endpoints de la API
│   ├── app.py         # Aplicación principal
│   ├── requirements.txt
│   └── venv/          # Entorno virtual
├── frontend/
│   ├── src/
│   │   ├── components/ # Componentes Vue
│   │   ├── views/      # Vistas
│   │   ├── store/      # Vuex store
│   │   ├── router/     # Vue Router
│   │   └── assets/     # Recursos estáticos
│   ├── package.json
│   └── node_modules/
├── docker-compose.yml
├── start_project.sh    # Script de inicio
└── README.md
```

## 🔧 Instalación y configuración

### Prerrequisitos
- Python 3.8+
- Node.js 14+
- npm o yarn

### Instalación rápida

1. Clonar el repositorio:
```bash
git clone [URL_DEL_REPOSITORIO]
cd visitor-registration
```

2. Ejecutar el script de inicio:
```bash
./start_project.sh
```

Este script automáticamente:
- Instala las dependencias del backend y frontend
- Configura los entornos virtuales
- Inicia ambos servidores
- Muestra las URLs de acceso

### Instalación manual

#### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

#### Frontend
```bash
cd frontend
npm install
npm run serve -- --port 8094
```

## 📡 API Endpoints

### Autenticación
- `POST /api/v1/auth/login` - Iniciar sesión

### Eventos
- `GET /api/v1/events/` - Listar todos los eventos
- `GET /api/v1/events/{id}` - Obtener evento específico
- `POST /api/v1/events/` - Crear evento (admin)
- `PUT /api/v1/events/{id}` - Actualizar evento (admin)
- `DELETE /api/v1/events/{id}` - Eliminar evento (admin)

### Visitantes
- `GET /api/v1/visitors/` - Listar visitantes (con paginación)
- `POST /api/v1/visitors/register` - Registrar nuevo visitante
- `GET /api/v1/visitors/statistics` - Obtener estadísticas
- `POST /api/v1/events/{event_id}/visitors` - Registrar visitante para evento

### Check-in
- `POST /api/v1/events/{event_id}/visitors/{visitor_id}/checkin` - Hacer check-in

## 🖥️ Interfaces de usuario

### Panel Administrativo
- URL: http://localhost:8094/admin
- Credenciales de prueba:
  - Usuario: admin
  - Contraseña: Admin123!

### Kiosco de registro
- URL: http://localhost:8094/kiosk
- Interfaz simplificada para autoregistro

### Página pública
- URL: http://localhost:8094/
- Vista de eventos disponibles

## 🗄️ Base de datos

### Modelos principales:
- **Event**: Eventos culturales
- **Visitor**: Información de visitantes
- **VisitorCheckIn**: Registro de asistencia
- **User**: Usuarios del sistema
- **Kiosk**: Kioscos de registro

## 🔐 Seguridad
- Autenticación basada en JWT (por implementar completamente)
- CORS configurado
- Validación de datos en frontend y backend
- Contraseñas hasheadas (por implementar)

## 🐛 Solución de problemas comunes

### El backend no inicia
1. Verificar que el puerto 8080 no esté en uso
2. Activar el entorno virtual: `source venv/bin/activate`
3. Instalar dependencias: `pip install -r requirements.txt`

### El frontend no se conecta al backend
1. Verificar que el backend esté corriendo en http://localhost:8080
2. Revisar la configuración en `.env.development`
3. Verificar CORS en el backend

### Error de base de datos
1. Eliminar archivos `*.db` en la carpeta backend
2. Reiniciar el backend para recrear las tablas

## 📝 Tareas pendientes
- [ ] Implementar autenticación JWT completa
- [ ] Migrar a PostgreSQL para producción
- [ ] Agregar sistema de notificaciones
- [ ] Implementar carga de imágenes para eventos
- [ ] Añadir exportación de reportes
- [ ] Completar tests unitarios
- [ ] Configurar CI/CD

## 🤝 Contribuir
1. Fork del proyecto
2. Crear rama de feature (`git checkout -b feature/NuevaCaracteristica`)
3. Commit de cambios (`git commit -m 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/NuevaCaracteristica`)
5. Crear Pull Request

## 📄 Licencia
Este proyecto es propiedad del Centro Cultural Banreservas.

## 👥 Equipo
- Desarrollo: [Tu nombre]
- Diseño: [Diseñador]
- Gestión: [Project Manager]

## 📞 Soporte
Para soporte técnico, contactar:
- Email: soporte@ccb.do
- Teléfono: 809-XXX-XXXX

---
Última actualización: Mayo 2025
