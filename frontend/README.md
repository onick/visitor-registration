# Frontend - Centro Cultural Banreservas

Este directorio contiene la aplicación frontend para la plataforma de gestión de eventos y visitantes del Centro Cultural Banreservas.

## Tecnologías utilizadas

- Vue.js 3
- Vuex para gestión de estado
- Vue Router para navegación
- Axios para comunicación con API

## Estructura del proyecto

```
/frontend
|-- /src
|   |-- /assets            # Archivos estáticos (CSS, imágenes)
|   |-- /components        # Componentes reutilizables
|   |   |-- /kiosk         # Componentes específicos para modo kiosco
|   |-- /layouts           # Layouts de la aplicación
|   |-- /router            # Configuración de rutas
|   |-- /services          # Servicios para API y utilidades
|   |-- /store             # Gestión de estado con Vuex
|   |   |-- /modules       # Módulos Vuex por funcionalidad
|   |-- /utils             # Funciones de utilidad
|   |-- /views             # Vistas/páginas de la aplicación
|   |   |-- /admin         # Vistas para el panel administrativo
|   |   |-- /auth          # Vistas de autenticación
|   |-- App.vue            # Componente raíz
|   |-- main.js            # Punto de entrada principal
|-- .env.development       # Variables de entorno para desarrollo
|-- vue.config.js          # Configuración de Vue
```

## Modos de la aplicación

El frontend tiene dos modos principales:

1. **Panel Administrativo**: Para gestión de eventos, visitantes y kioscos.
2. **Modo Kiosco**: Interfaz para el auto-registro de visitantes en los eventos.

## Requisitos previos

- Node.js v14.x o superior
- NPM v6.x o superior

## Instalación

1. Instala las dependencias:

```bash
npm install
```

2. Crea un archivo `.env.local` para configuraciones locales (opcional):

```bash
VUE_APP_API_URL=http://localhost:5000/api/v1
```

## Ejecución en modo desarrollo

```bash
npm run serve
```

La aplicación estará disponible en: http://localhost:8080

## Compilación para producción

```bash
npm run build
```

Los archivos compilados se generarán en el directorio `/dist`.

## Linting y corrección de archivos

```bash
npm run lint
```

## Pruebas

```bash
# Ejecutar pruebas unitarias
npm run test:unit

# Ejecutar pruebas e2e
npm run test:e2e
```

## Personalización

La configuración de Vue puede ser modificada en el archivo `vue.config.js`.

## Documentación adicional

- [Vue.js](https://vuejs.org/)
- [Vuex](https://vuex.vuejs.org/)
- [Vue Router](https://router.vuejs.org/)
- [Axios](https://axios-http.com/) 