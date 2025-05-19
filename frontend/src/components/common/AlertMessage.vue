<template>
  <transition name="alert-fade">
    <div 
      v-if="isVisible" 
      class="alert" 
      :class="[
        `alert-${type}`, 
        {
          'is-dismissible': dismissible,
          'with-icon': showIcon,
          'is-outlined': outlined,
          'is-bordered': bordered
        }
      ]"
      role="alert"
    >
      <div v-if="showIcon" class="alert-icon">
        <i :class="getIcon"></i>
      </div>
      
      <div class="alert-content">
        <div v-if="title" class="alert-title">{{ title }}</div>
        <div class="alert-message">
          <slot>{{ message }}</slot>
        </div>
      </div>
      
      <button 
        v-if="dismissible" 
        type="button" 
        class="alert-close" 
        @click="dismiss"
        aria-label="Cerrar"
      >
        <i class="fas fa-times"></i>
      </button>
    </div>
  </transition>
</template>

<script>
export default {
  name: 'AlertMessage',
  props: {
    type: {
      type: String,
      default: 'primary',
      validator: value => ['primary', 'success', 'danger', 'warning', 'info', 'light', 'dark'].includes(value)
    },
    message: {
      type: String,
      default: ''
    },
    title: {
      type: String,
      default: ''
    },
    dismissible: {
      type: Boolean,
      default: false
    },
    showIcon: {
      type: Boolean,
      default: true
    },
    autoDismiss: {
      type: [Boolean, Number],
      default: false
    },
    value: {
      type: Boolean,
      default: true
    },
    outlined: {
      type: Boolean,
      default: false
    },
    bordered: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      isVisible: this.value,
      dismissTimeout: null
    };
  },
  computed: {
    getIcon() {
      switch (this.type) {
        case 'success':
          return 'fas fa-check-circle';
        case 'danger':
          return 'fas fa-exclamation-circle';
        case 'warning':
          return 'fas fa-exclamation-triangle';
        case 'info':
          return 'fas fa-info-circle';
        default:
          return 'fas fa-bell';
      }
    }
  },
  watch: {
    value(newValue) {
      this.isVisible = newValue;
      
      if (newValue && this.autoDismiss) {
        this.setAutoDismiss();
      }
    },
    autoDismiss(newValue) {
      if (newValue && this.isVisible) {
        this.setAutoDismiss();
      } else {
        this.clearAutoDismiss();
      }
    }
  },
  mounted() {
    if (this.isVisible && this.autoDismiss) {
      this.setAutoDismiss();
    }
  },
  beforeUnmount() {
    if (this.dismissTimeout) {
      clearTimeout(this.dismissTimeout);
    }
  },
  methods: {
    dismiss() {
      this.isVisible = false;
      this.$emit('input', false);
      this.$emit('dismiss');
      this.clearAutoDismiss();
    },
    setAutoDismiss() {
      this.clearAutoDismiss();
      
      const duration = typeof this.autoDismiss === 'number' ? this.autoDismiss : 5000;
      
      this.dismissTimeout = setTimeout(() => {
        this.dismiss();
      }, duration);
    },
    clearAutoDismiss() {
      if (this.dismissTimeout) {
        clearTimeout(this.dismissTimeout);
        this.dismissTimeout = null;
      }
    }
  }
};
</script>

<style scoped>
.alert {
  display: flex;
  align-items: flex-start;
  padding: 12px 16px;
  margin-bottom: 16px;
  border-radius: 6px;
  position: relative;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.alert-content {
  flex: 1;
}

.alert-title {
  margin-bottom: 4px;
  font-weight: 600;
  font-size: 15px;
}

.alert-message {
  font-size: 14px;
}

/* Tipos de alertas */
.alert-primary {
  background-color: #eae4f5;
  color: #512da8;
  border-left: 4px solid #512da8;
}

.alert-success {
  background-color: #e6f4e8;
  color: #43a047;
  border-left: 4px solid #43a047;
}

.alert-danger {
  background-color: #fbe6e6;
  color: #e53935;
  border-left: 4px solid #e53935;
}

.alert-warning {
  background-color: #fff5e0;
  color: #ff9800;
  border-left: 4px solid #ff9800;
}

.alert-info {
  background-color: #e3f2fd;
  color: #039be5;
  border-left: 4px solid #039be5;
}

.alert-light {
  background-color: #f8f9fa;
  color: #495057;
  border-left: 4px solid #ced4da;
}

.alert-dark {
  background-color: #e9ecef;
  color: #343a40;
  border-left: 4px solid #343a40;
}

/* Variante outline */
.is-outlined {
  background-color: transparent;
  border: 1px solid;
}

.is-outlined.alert-primary {
  border-color: #512da8;
  border-left-width: 4px;
}

.is-outlined.alert-success {
  border-color: #43a047;
  border-left-width: 4px;
}

.is-outlined.alert-danger {
  border-color: #e53935;
  border-left-width: 4px;
}

.is-outlined.alert-warning {
  border-color: #ff9800;
  border-left-width: 4px;
}

.is-outlined.alert-info {
  border-color: #039be5;
  border-left-width: 4px;
}

.is-outlined.alert-light {
  border-color: #ced4da;
  border-left-width: 4px;
}

.is-outlined.alert-dark {
  border-color: #343a40;
  border-left-width: 4px;
}

/* Variante con borde */
.is-bordered {
  border: 1px solid;
}

.is-bordered.alert-primary {
  border-color: #d1c4e9;
}

.is-bordered.alert-success {
  border-color: #c8e6c9;
}

.is-bordered.alert-danger {
  border-color: #ffcdd2;
}

.is-bordered.alert-warning {
  border-color: #ffe0b2;
}

.is-bordered.alert-info {
  border-color: #b3e5fc;
}

.is-bordered.alert-light {
  border-color: #e9ecef;
}

.is-bordered.alert-dark {
  border-color: #ced4da;
}

/* Icono */
.alert-icon {
  font-size: 20px;
  display: flex;
  align-items: center;
  margin-right: 12px;
}

.with-icon {
  padding-left: 16px;
}

/* Botón cerrar */
.alert-close {
  border: none;
  background: transparent;
  font-size: 14px;
  cursor: pointer;
  opacity: 0.6;
  padding: 4px;
  margin-left: 12px;
  border-radius: 4px;
  color: inherit;
  display: flex;
  align-items: center;
  justify-content: center;
}

.alert-close:hover {
  opacity: 1;
  background-color: rgba(0, 0, 0, 0.05);
}

.alert-close:focus {
  outline: none;
}

/* Animaciones */
.alert-fade-enter-active,
.alert-fade-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}

.alert-fade-enter,
.alert-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style> 