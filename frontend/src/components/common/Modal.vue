<template>
  <transition name="modal-fade">
    <div v-if="isVisible" class="modal-overlay" @click.self="onOverlayClick">
      <div 
        class="modal-container" 
        :class="[
          `size-${size}`, 
          { 
            'has-footer': $slots.footer || (showFooter && (showCloseBtn || showConfirmBtn)),
            'no-padding': noPadding
          }
        ]"
        :style="{ maxWidth: customWidth || undefined }"
      >
        <!-- Cabecera del modal -->
        <div v-if="$slots.header || title" class="modal-header">
          <slot name="header">
            <h3 class="modal-title">{{ title }}</h3>
            <button v-if="showCloseX" class="modal-close" @click="close">
              <i class="fas fa-times"></i>
            </button>
          </slot>
        </div>
        
        <!-- Contenido del modal -->
        <div class="modal-body" :class="{ 'has-scroll': scroll }">
          <slot></slot>
        </div>
        
        <!-- Pie del modal -->
        <div v-if="$slots.footer || (showFooter && (showCloseBtn || showConfirmBtn))" class="modal-footer">
          <slot name="footer">
            <div class="modal-actions">
              <button 
                v-if="showCloseBtn" 
                class="btn btn-light" 
                @click="close"
              >
                {{ closeText }}
              </button>
              <button 
                v-if="showConfirmBtn" 
                class="btn btn-primary" 
                :class="{ 'is-loading': loading }" 
                :disabled="loading" 
                @click="confirm"
              >
                {{ confirmText }}
              </button>
            </div>
          </slot>
        </div>
      </div>
    </div>
  </transition>
</template>

<script>
export default {
  name: 'AppModal',
  props: {
    value: {
      type: Boolean,
      default: false
    },
    title: {
      type: String,
      default: ''
    },
    size: {
      type: String,
      default: 'medium',
      validator: value => ['small', 'medium', 'large', 'full', 'auto'].includes(value)
    },
    customWidth: {
      type: String,
      default: ''
    },
    closeOnClickOutside: {
      type: Boolean,
      default: true
    },
    escapeClose: {
      type: Boolean,
      default: true
    },
    showCloseX: {
      type: Boolean,
      default: true
    },
    showFooter: {
      type: Boolean,
      default: true
    },
    showCloseBtn: {
      type: Boolean,
      default: true
    },
    showConfirmBtn: {
      type: Boolean,
      default: false
    },
    closeText: {
      type: String,
      default: 'Cerrar'
    },
    confirmText: {
      type: String,
      default: 'Confirmar'
    },
    loading: {
      type: Boolean,
      default: false
    },
    scroll: {
      type: Boolean,
      default: false
    },
    noPadding: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      isVisible: this.value
    };
  },
  watch: {
    value(newVal) {
      this.isVisible = newVal;
      
      if (newVal) {
        this.addEventListeners();
        document.body.classList.add('modal-open');
      } else {
        this.removeEventListeners();
        document.body.classList.remove('modal-open');
      }
    }
  },
  mounted() {
    if (this.isVisible) {
      this.addEventListeners();
      document.body.classList.add('modal-open');
    }
  },
  beforeUnmount() {
    this.removeEventListeners();
    document.body.classList.remove('modal-open');
  },
  methods: {
    onOverlayClick() {
      if (this.closeOnClickOutside) {
        this.close();
      }
    },
    close() {
      this.isVisible = false;
      this.$emit('input', false);
      this.$emit('close');
    },
    confirm() {
      this.$emit('confirm');
    },
    handleEscapeKey(event) {
      if (this.escapeClose && event.key === 'Escape' && this.isVisible) {
        this.close();
      }
    },
    addEventListeners() {
      document.addEventListener('keydown', this.handleEscapeKey);
    },
    removeEventListeners() {
      document.removeEventListener('keydown', this.handleEscapeKey);
    }
  }
};
</script>

<style scoped>
/* Estilos globales (se deben agregar a tu archivo CSS principal) */
:global(body.modal-open) {
  overflow: hidden;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  overflow-y: auto;
  padding: 20px;
}

.modal-container {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  width: 100%;
  max-height: calc(100vh - 40px);
  position: relative;
  margin: auto;
}

/* Tamaños */
.size-small {
  max-width: 400px;
}

.size-medium {
  max-width: 600px;
}

.size-large {
  max-width: 800px;
}

.size-full {
  max-width: 100%;
  height: calc(100vh - 40px);
  border-radius: 0;
}

.size-auto {
  max-width: auto;
}

.modal-header {
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-title {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
  color: #333;
}

.modal-close {
  background: transparent;
  border: none;
  font-size: 16px;
  cursor: pointer;
  color: #666;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s;
}

.modal-close:hover {
  background-color: #f0f0f0;
  color: #333;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.modal-body.has-scroll {
  max-height: 60vh;
}

.no-padding .modal-body {
  padding: 0;
}

.modal-footer {
  padding: 16px 20px;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
}

.modal-actions {
  display: flex;
  gap: 10px;
}

/* Animación de entrada/salida */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: all 0.3s;
}

.modal-fade-enter-active .modal-container,
.modal-fade-leave-active .modal-container {
  transition: all 0.3s;
}

.modal-fade-enter,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter .modal-container,
.modal-fade-leave-to .modal-container {
  transform: translateY(20px);
  opacity: 0;
}

/* Estilos para botones (puedes eliminar si ya tienes componentes de botones) */
.btn {
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn-primary {
  background-color: #512da8;
  color: white;
  border-color: #512da8;
}

.btn-primary:hover:not(:disabled) {
  background-color: #4527a0;
  border-color: #4527a0;
}

.btn-light {
  background-color: #f5f5f5;
  color: #333;
  border-color: #e0e0e0;
}

.btn-light:hover:not(:disabled) {
  background-color: #e0e0e0;
}

.btn:disabled,
.btn.is-loading {
  opacity: 0.7;
  cursor: not-allowed;
}

.is-loading {
  position: relative;
}

.is-loading::after {
  content: "";
  position: absolute;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #fff;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style> 