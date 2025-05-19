# Sistema de Registro de Visitantes - CCB

## Resumen de Cambios Implementados

### 1. Código de Registro Único
- ✅ Agregado campo `registration_code` al modelo `Visitor`
- ✅ Generación automática de códigos alfanuméricos de 6 caracteres
- ✅ Actualizado endpoint de registro para incluir el código
- ✅ Actualizada función de verificación para aceptar el código único
- ✅ Creado script de migración para visitantes existentes

### 2. Actualización de Colores del Panel
- ✅ Colores principales del CCB aplicados:
  - Primario: #F99D2A (Naranja/Dorado)
  - Secundario: #00BDF2 (Azul brillante)
  - Oscuro: #474C55 (Gris oscuro)
- ✅ Dashboard actualizado con nuevos colores
- ✅ Tarjetas de eventos con colores CCB
- ✅ Archivo theme.css creado para aplicación global
- ✅ Vista de confirmación actualizada con colores CCB

### 3. Funcionalidades del Sistema

#### Sistema de Códigos
- Los visitantes reciben un código único al registrarse
- Múltiples métodos de verificación:
  - Código de registro único
  - Email
  - Teléfono
  - ID numérico

#### Interfaz de Usuario
- Dashboard con estadísticas en tiempo real
- Gestión de eventos mejorada
- Vista de confirmación con código de registro
- Colores coherentes con la marca CCB

## Estructura de Archivos Modificados

### Backend
- `/models/visitor.py` - Modelo actualizado con código de registro
- `/app.py` - Endpoints actualizados
- `/add_registration_code.py` - Script de migración
- `/test_registration_codes.py` - Script de pruebas
- `/docs/REGISTRATION_CODES.md` - Documentación del sistema

### Frontend
- `/src/views/admin/Dashboard.vue` - Colores actualizados
- `/src/views/admin/Events.vue` - Colores actualizados
- `/src/views/ConfirmationView.vue` - Muestra código de registro
- `/src/views/RegistrationView.vue` - Maneja código de registro
- `/src/store/modules/visitors.js` - Store actualizado
- `/src/assets/styles/theme.css` - Tema global CCB
- `/src/main.js` - Importa tema global

## Cómo Ejecutar

### 1. Backend
```bash
cd backend
# Ejecutar migración para agregar códigos
python add_registration_code.py
# Iniciar servidor
python app.py
```

### 2. Frontend
```bash
cd frontend
npm install
npm run serve
```

### 3. Pruebas
```bash
cd backend
# Probar sistema de códigos
python test_registration_codes.py
```

## Flujo de Usuario Actualizado

1. **Registro**
   - Visitante completa formulario
   - Sistema genera código único (ej: "ABC123")
   - Se muestra en pantalla de confirmación

2. **Check-in**
   - Visitante puede usar:
     - Código único de 6 caracteres
     - Email
     - Teléfono
   - Sistema verifica y muestra eventos disponibles

3. **Panel de Administración**
   - Dashboard con colores CCB
   - Estadísticas en tiempo real
   - Gestión de eventos y visitantes

## Próximos Pasos Recomendados

### Corto Plazo
1. **Sistema de Notificaciones Email**
   - Enviar código por email tras registro
   - Recordatorios de eventos
   - Confirmaciones de check-in

2. **Exportación de Datos**
   - Exportar visitantes a CSV/Excel
   - Filtros avanzados
   - Reportes por evento

3. **Mejoras de UI/UX**
   - Animaciones y transiciones
   - Modo oscuro opcional
   - Versión móvil optimizada

### Mediano Plazo
1. **Gráficos y Analíticas**
   - Dashboard con gráficos interactivos
   - Tendencias de asistencia
   - Métricas por evento

2. **Sistema de Permisos**
   - Roles de usuario más granulares
   - Permisos por evento
   - Auditoría de acciones

3. **Integración con Calendarios**
   - Exportar eventos a Google Calendar
   - Sincronización con Outlook
   - Recordatorios automáticos

### Largo Plazo
1. **App Móvil Nativa**
   - Aplicación para iOS/Android
   - Check-in offline
   - Notificaciones push

2. **Reconocimiento Facial**
   - Check-in automático
   - Seguridad mejorada
   - Análisis de flujo de visitantes

3. **API Pública**
   - Integración con otros sistemas
   - Webhooks para eventos
   - SDK para desarrolladores

## Comandos Útiles

### Backend
```bash
# Crear base de datos
python init_db.py

# Ejecutar migración
python add_registration_code.py

# Crear visitantes de prueba
python create_test_visitors.py

# Probar códigos
python test_registration_codes.py
```

### Frontend
```bash
# Instalar dependencias
npm install

# Ejecutar en desarrollo
npm run serve

# Construir para producción
npm run build

# Ejecutar tests
npm run test
```

## Configuración de Producción

### Variables de Entorno Backend
```env
FLASK_ENV=production
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email
MAIL_PASSWORD=your-password
```

### Variables de Entorno Frontend
```env
VUE_APP_API_URL=https://api.ccb.do
VUE_APP_KIOSK_ID=1
VUE_APP_ENV=production
```

## Documentación

- [Códigos de Registro](docs/REGISTRATION_CODES.md)
- [API Reference](docs/API.md)
- [Guía de Instalación](docs/INSTALLATION.md)
- [Manual de Usuario](docs/USER_MANUAL.md)

## Soporte

Para reportar problemas o solicitar nuevas funcionalidades:
- Email: soporte@ccb.do
- Teléfono: 809-XXX-XXXX
- Sistema de tickets: https://soporte.ccb.do
