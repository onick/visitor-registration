# Guía de Colores - Centro Cultural Banreservas

## Paleta de Colores Oficial

El sistema utiliza los siguientes colores corporativos:

### Colores Principales

1. **Primario (Naranja/Dorado)**: `#F99D2A`
   - Variante Clara: `#FDB757`
   - Variante Oscura: `#E68A1A`
   - Uso: Botones principales, acentos importantes, estadísticas destacadas

2. **Secundario (Azul Brillante)**: `#00BDF2`
   - Variante Clara: `#33CDF5`
   - Variante Oscura: `#0099CC`
   - Uso: Links, botones secundarios, iconos informativos

3. **Oscuro (Gris Oscuro)**: `#474C55`
   - Variante Media: `#5A5F69`
   - Variante Clara: `#7A7F88`
   - Uso: Textos principales, encabezados, bordes

### Colores de Estado

- **Éxito**: `#28A745` (Verde)
- **Advertencia**: `#F99D2A` (Usa el color primario)
- **Peligro**: `#DC3545` (Rojo)
- **Información**: `#00BDF2` (Usa el color secundario)

## Implementación

### Variables CSS

Las variables de color están definidas en `/frontend/src/assets/styles/colors.css`:

```css
:root {
  --color-primary: #F99D2A;
  --color-secondary: #00BDF2;
  --color-dark: #474C55;
  /* ... más variables */
}
```

### Uso en Componentes

Para usar los colores en componentes Vue:

```css
.mi-elemento {
  color: var(--color-primary);
  background-color: var(--color-secondary);
}
```

### Clases de Utilidad

```css
.text-primary { color: var(--color-primary); }
.bg-primary { background-color: var(--color-primary); }
.btn-primary { background-color: var(--color-primary); }
```

## Aplicación en el Sistema

### 1. Botones

- **Primarios**: Fondo naranja/dorado con texto blanco
- **Secundarios**: Fondo azul brillante con texto blanco
- **Oscuros**: Fondo gris oscuro con texto blanco

### 2. Encabezados

- **H1**: Color gris oscuro (`--color-dark`)
- **H2-H6**: Variaciones del gris oscuro

### 3. Textos

- **Principal**: Gris oscuro (`--color-text`)
- **Secundario**: Gris claro (`--color-text-light`)
- **Enlaces**: Azul brillante (`--color-secondary`)

### 4. Fondos

- **Principal**: Blanco (`#FFFFFF`)
- **Secundario**: Gris muy claro (`#F8F9FA`)
- **Tarjetas**: Blanco con sombras suaves

### 5. Iconos

- **Principales**: Color primario para destacar
- **Informativos**: Color secundario
- **Neutros**: Gris oscuro

## Componentes Actualizados

1. **Gestión de Eventos** (`Events.vue`)
   - Botones con color primario
   - Enlaces con color secundario
   - Iconos de estadísticas en color primario

2. **Gestión de Kioscos** (`Kiosks.vue`)
   - Encabezados en gris oscuro
   - Botones con colores apropiados
   - Indicadores de estado en verde/rojo

## Mantenimiento

Para mantener consistencia visual:

1. Siempre usar variables CSS, nunca colores hardcodeados
2. Seguir las convenciones de nombres establecidas
3. Actualizar variables en un solo lugar
4. Probar cambios en diferentes componentes

## Accesibilidad

Los colores seleccionados cumplen con estándares de accesibilidad:
- Contraste adecuado entre texto y fondo
- Colores distinguibles para usuarios con daltonismo
- Feedback visual claro en estados interactivos

## Próximos Pasos

1. Actualizar todos los componentes restantes
2. Crear temas alternativos (modo oscuro)
3. Documentar casos de uso específicos
4. Crear guía visual completa
