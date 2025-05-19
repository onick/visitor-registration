<template>
  <div class="card" :class="[`elevation-${elevation}`, { 'no-padding': noPadding }]">
    <!-- Encabezado de la tarjeta (opcional) -->
    <div v-if="$slots.header || title" class="card-header">
      <slot name="header">
        <div class="card-header-content">
          <h3 v-if="title" class="card-title">{{ title }}</h3>
          <p v-if="subtitle" class="card-subtitle">{{ subtitle }}</p>
        </div>
        <div v-if="$slots.headerActions" class="card-header-actions">
          <slot name="headerActions"></slot>
        </div>
      </slot>
    </div>
    
    <!-- Imagen de la tarjeta (opcional) -->
    <div v-if="$slots.image || image" class="card-image">
      <slot name="image">
        <img :src="image" :alt="imageAlt || title" />
      </slot>
    </div>
    
    <!-- Contenido de la tarjeta -->
    <div class="card-body" :class="{ 'has-divider': $slots.header || title || $slots.image || image }">
      <slot></slot>
    </div>
    
    <!-- Pie de la tarjeta (opcional) -->
    <div v-if="$slots.footer" class="card-footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AppCard',
  props: {
    title: {
      type: String,
      default: ''
    },
    subtitle: {
      type: String,
      default: ''
    },
    image: {
      type: String,
      default: ''
    },
    imageAlt: {
      type: String,
      default: ''
    },
    elevation: {
      type: Number,
      default: 1,
      validator: (value) => value >= 0 && value <= 5
    },
    noPadding: {
      type: Boolean,
      default: false
    }
  }
};
</script>

<style scoped>
.card {
  background-color: #fff;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  width: 100%;
}

/* Niveles de elevación */
.elevation-0 {
  box-shadow: none;
  border: 1px solid #eee;
}

.elevation-1 {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.elevation-2 {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.elevation-3 {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
}

.elevation-4 {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.14);
}

.elevation-5 {
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.16);
}

/* Encabezado de la tarjeta */
.card-header {
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #eee;
}

.card-header-content {
  flex: 1;
}

.card-title {
  font-size: 18px;
  font-weight: 500;
  color: #333;
  margin: 0;
}

.card-subtitle {
  font-size: 14px;
  color: #666;
  margin: 4px 0 0 0;
}

.card-header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Imagen de la tarjeta */
.card-image {
  width: 100%;
  position: relative;
  overflow: hidden;
}

.card-image img {
  width: 100%;
  display: block;
  height: auto;
}

/* Cuerpo de la tarjeta */
.card-body {
  padding: 20px;
  flex: 1;
}

.card-body.has-divider {
  border-top: none;
}

.no-padding .card-body {
  padding: 0;
}

/* Pie de la tarjeta */
.card-footer {
  padding: 16px 20px;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 10px;
}
</style> 