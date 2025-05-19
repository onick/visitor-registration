<template>
  <div class="form-validator">
    <slot
      :validate="validate"
      :errors="errors"
      :isValid="isValid"
      :validateField="validateField"
      :resetValidation="resetValidation"
    ></slot>
  </div>
</template>

<script>
export default {
  name: 'FormValidator',
  props: {
    rules: {
      type: Object,
      required: true
    },
    initialValues: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      values: { ...this.initialValues },
      errors: {},
      touched: {},
      isSubmitting: false
    };
  },
  computed: {
    isValid() {
      return Object.keys(this.errors).length === 0;
    }
  },
  methods: {
    /**
     * Valida un campo específico
     * @param {string} fieldName - Nombre del campo a validar
     * @param {any} value - Valor del campo
     * @returns {string|null} Mensaje de error o null si es válido
     */
    validateField(fieldName, value) {
      const fieldRules = this.rules[fieldName];
      if (!fieldRules) return null;

      // Marcar campo como tocado
      this.touched[fieldName] = true;
      
      // Validar reglas
      for (const rule of fieldRules) {
        const error = rule(value, this.values);
        if (error) {
          this.$set(this.errors, fieldName, error);
          return error;
        }
      }
      
      // Si no hay errores, eliminar error existente
      if (this.errors[fieldName]) {
        this.$delete(this.errors, fieldName);
      }
      
      return null;
    },
    
    /**
     * Valida todos los campos del formulario
     * @param {Object} values - Valores del formulario
     * @returns {boolean} True si el formulario es válido
     */
    validate(values) {
      this.values = values;
      this.errors = {};
      
      // Validar cada campo
      Object.keys(this.rules).forEach(fieldName => {
        const value = values[fieldName];
        const error = this.validateField(fieldName, value);
        if (error) {
          this.errors[fieldName] = error;
        }
      });
      
      // Emitir evento con resultado de validación
      this.$emit('validation', {
        isValid: this.isValid,
        errors: this.errors,
        values: this.values
      });
      
      return this.isValid;
    },
    
    /**
     * Reinicia la validación
     */
    resetValidation() {
      this.errors = {};
      this.touched = {};
      this.isSubmitting = false;
    }
  }
};
</script>

<style scoped>
.form-validator {
  width: 100%;
}

/* Estilos para mensajes de error que pueden ser usados por componentes hijos */
:deep(.error-message) {
  color: #f56c6c;
  font-size: 12px;
  margin-top: 4px;
  display: block;
}

:deep(.form-group) {
  margin-bottom: 16px;
}

:deep(.form-control) {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.2s;
}

:deep(.form-control:focus) {
  outline: none;
  border-color: #409eff;
}

:deep(.form-control.is-invalid) {
  border-color: #f56c6c;
}

:deep(.form-label) {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

:deep(.required-mark) {
  color: #f56c6c;
  margin-left: 4px;
}
</style>