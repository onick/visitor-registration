<template>
  <component
    :is="tag"
    :class="[
      'btn',
      `btn-${variant}`,
      `size-${size}`,
      { 
        'is-rounded': rounded,
        'is-block': block,
        'is-loading': loading,
        'is-disabled': disabled || loading,
        'has-icon': !!icon && !iconRight,
        'has-icon-right': !!icon && iconRight
      }
    ]"
    :disabled="disabled || loading"
    :type="nativeType"
    :href="tag === 'a' ? href : undefined"
    :target="tag === 'a' ? target : undefined"
    :to="tag === 'router-link' ? to : undefined"
    @click="onClick"
  >
    <span v-if="loading" class="spinner">
      <i class="fas fa-spinner fa-spin"></i>
    </span>
    
    <span v-if="icon && !iconRight" class="icon left-icon">
      <i :class="icon"></i>
    </span>
    
    <span v-if="$slots.default" class="btn-content">
      <slot></slot>
    </span>
    
    <span v-if="icon && iconRight" class="icon right-icon">
      <i :class="icon"></i>
    </span>
  </component>
</template>

<script>
export default {
  name: 'AppButton',
  props: {
    variant: {
      type: String,
      default: 'primary',
      validator: (value) => [
        'primary', 'secondary', 'success', 'danger',
        'warning', 'info', 'light', 'dark', 'link',
        'outline-primary', 'outline-secondary', 'outline-success',
        'outline-danger', 'outline-warning', 'outline-info',
        'outline-light', 'outline-dark'
      ].includes(value)
    },
    size: {
      type: String,
      default: 'medium',
      validator: (value) => ['small', 'medium', 'large'].includes(value)
    },
    nativeType: {
      type: String,
      default: 'button',
      validator: (value) => ['button', 'submit', 'reset'].includes(value)
    },
    disabled: {
      type: Boolean,
      default: false
    },
    loading: {
      type: Boolean,
      default: false
    },
    rounded: {
      type: Boolean,
      default: false
    },
    block: {
      type: Boolean,
      default: false
    },
    tag: {
      type: String,
      default: 'button',
      validator: (value) => ['button', 'a', 'router-link'].includes(value)
    },
    href: {
      type: String,
      default: undefined
    },
    target: {
      type: String,
      default: undefined
    },
    to: {
      type: [String, Object],
      default: undefined
    },
    icon: {
      type: String,
      default: ''
    },
    iconRight: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    onClick(event) {
      if (this.disabled || this.loading) {
        event.preventDefault();
        return;
      }
      
      this.$emit('click', event);
    }
  }
};
</script>

<style scoped>
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0 16px;
  font-weight: 500;
  text-align: center;
  white-space: nowrap;
  vertical-align: middle;
  user-select: none;
  border: 1px solid transparent;
  border-radius: 4px;
  transition: all 0.2s ease-in-out;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  text-decoration: none;
  line-height: 1;
}

.btn:focus {
  outline: 0;
  box-shadow: 0 0 0 3px rgba(81, 45, 168, 0.25);
}

.btn-content {
  position: relative;
  z-index: 2;
}

/* Tamaños */
.size-small {
  height: 32px;
  font-size: 12px;
}

.size-medium {
  height: 40px;
  font-size: 14px;
}

.size-large {
  height: 48px;
  font-size: 16px;
}

/* Variantes */
.btn-primary {
  background-color: #512da8;
  color: white;
  border-color: #512da8;
}

.btn-primary:hover:not(.is-disabled) {
  background-color: #4527a0;
  border-color: #4527a0;
}

.btn-secondary {
  background-color: #757575;
  color: white;
  border-color: #757575;
}

.btn-secondary:hover:not(.is-disabled) {
  background-color: #616161;
  border-color: #616161;
}

.btn-success {
  background-color: #43a047;
  color: white;
  border-color: #43a047;
}

.btn-success:hover:not(.is-disabled) {
  background-color: #388e3c;
  border-color: #388e3c;
}

.btn-danger {
  background-color: #e53935;
  color: white;
  border-color: #e53935;
}

.btn-danger:hover:not(.is-disabled) {
  background-color: #d32f2f;
  border-color: #d32f2f;
}

.btn-warning {
  background-color: #ffb300;
  color: #333;
  border-color: #ffb300;
}

.btn-warning:hover:not(.is-disabled) {
  background-color: #ffa000;
  border-color: #ffa000;
}

.btn-info {
  background-color: #039be5;
  color: white;
  border-color: #039be5;
}

.btn-info:hover:not(.is-disabled) {
  background-color: #0288d1;
  border-color: #0288d1;
}

.btn-light {
  background-color: #f5f5f5;
  color: #333;
  border-color: #e0e0e0;
}

.btn-light:hover:not(.is-disabled) {
  background-color: #e0e0e0;
  border-color: #d5d5d5;
}

.btn-dark {
  background-color: #424242;
  color: white;
  border-color: #424242;
}

.btn-dark:hover:not(.is-disabled) {
  background-color: #303030;
  border-color: #303030;
}

.btn-link {
  background-color: transparent;
  color: #512da8;
  border-color: transparent;
  text-decoration: none;
  box-shadow: none;
}

.btn-link:hover:not(.is-disabled) {
  color: #4527a0;
  text-decoration: underline;
  background-color: transparent;
  border-color: transparent;
}

/* Outline buttons */
.btn-outline-primary {
  background-color: transparent;
  color: #512da8;
  border-color: #512da8;
}

.btn-outline-primary:hover:not(.is-disabled) {
  background-color: #512da8;
  color: white;
}

.btn-outline-secondary {
  background-color: transparent;
  color: #757575;
  border-color: #757575;
}

.btn-outline-secondary:hover:not(.is-disabled) {
  background-color: #757575;
  color: white;
}

.btn-outline-success {
  background-color: transparent;
  color: #43a047;
  border-color: #43a047;
}

.btn-outline-success:hover:not(.is-disabled) {
  background-color: #43a047;
  color: white;
}

.btn-outline-danger {
  background-color: transparent;
  color: #e53935;
  border-color: #e53935;
}

.btn-outline-danger:hover:not(.is-disabled) {
  background-color: #e53935;
  color: white;
}

.btn-outline-warning {
  background-color: transparent;
  color: #ffb300;
  border-color: #ffb300;
}

.btn-outline-warning:hover:not(.is-disabled) {
  background-color: #ffb300;
  color: #333;
}

.btn-outline-info {
  background-color: transparent;
  color: #039be5;
  border-color: #039be5;
}

.btn-outline-info:hover:not(.is-disabled) {
  background-color: #039be5;
  color: white;
}

.btn-outline-light {
  background-color: transparent;
  color: #757575;
  border-color: #e0e0e0;
}

.btn-outline-light:hover:not(.is-disabled) {
  background-color: #f5f5f5;
  color: #333;
}

.btn-outline-dark {
  background-color: transparent;
  color: #424242;
  border-color: #424242;
}

.btn-outline-dark:hover:not(.is-disabled) {
  background-color: #424242;
  color: white;
}

/* Estados */
.is-disabled {
  opacity: 0.65;
  cursor: not-allowed;
  pointer-events: none;
}

.is-loading {
  pointer-events: none;
}

.is-loading .btn-content,
.is-loading .icon {
  visibility: hidden;
}

.spinner {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 3;
}

/* Modificadores */
.is-rounded {
  border-radius: 50px;
}

.is-block {
  display: flex;
  width: 100%;
}

/* Iconos */
.icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

.left-icon {
  margin-right: 8px;
}

.right-icon {
  margin-left: 8px;
}

.has-icon:not(.has-icon-right) {
  padding-left: 12px;
}

.has-icon-right {
  padding-right: 12px;
}
</style> 