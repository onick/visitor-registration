# Sistema de Kioscos - Centro Cultural Banreservas

## Resumen de Implementación

Se han configurado dos kioscos específicos para el Centro Cultural Banreservas:

### 1. Kiosco Entrada Principal
- **Propósito**: Punto principal de registro y check-in
- **Ubicación**: Entrada principal del edificio
- **Funciones**: 
  - Registro de nuevos visitantes
  - Check-in de visitantes registrados
  - Información de eventos

### 2. Kiosco Sala VR
- **Propósito**: Gestión de visitantes para experiencias VR
- **Ubicación**: Sala de Realidad Virtual
- **Funciones**:
  - Registro para experiencias VR
  - Check-in para sesiones programadas
  - Control de turnos

## Cambios Realizados

### Backend
1. Script `setup_kiosks.py` para configurar los dos kioscos
2. Configuración específica para cada ubicación
3. Parámetros personalizados por kiosco

### Frontend
1. Vista actualizada mostrando solo los dos kioscos
2. Funcionalidad de gestión remota
3. Indicadores de estado en tiempo real
4. Acciones de control (activar/desactivar, reiniciar, configurar)

## Características Principales

### Gestión Remota
- Activar/Desactivar kioscos
- Reinicio remoto
- Configuración de parámetros
- Monitoreo de estado

### Estadísticas
- Conteo de registros
- Conteo de check-ins
- Último acceso registrado
- Estado online/offline

### Configuración
- Idioma (español por defecto)
- Tiempo de inactividad
- Mensajes personalizados
- Filtros de eventos

## Cómo Usar

### 1. Configurar Kioscos
```bash
cd backend
python setup_kiosks.py
```

### 2. Verificar en Panel Admin
- Ir a `/admin/kiosks`
- Ver los dos kioscos configurados
- Verificar estado y estadísticas

### 3. Operaciones Disponibles
- **Activar/Desactivar**: Controla si el kiosco está disponible
- **Reiniciar**: Reinicio remoto del sistema
- **Configurar**: Ajustar parámetros del kiosco

## Estados de Kioscos

### Online (Verde)
- Comunicación activa
- Última actividad < 5 minutos
- Funcionando correctamente

### Offline (Rojo)
- Sin comunicación reciente
- Última actividad > 5 minutos
- Requiere atención

### Inactivo (Gris)
- Desactivado manualmente
- No disponible para usuarios
- En mantenimiento

## Próximos Pasos

1. Configurar hardware físico de kioscos
2. Instalar aplicación en dispositivos
3. Conectar a la red del centro
4. Realizar pruebas de funcionamiento
5. Capacitar al personal

## Documentación

- [Configuración Completa](KIOSKS_CONFIGURATION.md)
- [Manual de Usuario](KIOSKS_USER_MANUAL.md)
- [Guía de Solución de Problemas](KIOSKS_TROUBLESHOOTING.md)

## Notas Técnicas

- Los kioscos se comunican via API REST
- Heartbeat cada 60 segundos
- Timeout configurable por kiosco
- Logs de actividad almacenados

La implementación está lista para su despliegue en los dispositivos físicos del Centro Cultural Banreservas.
