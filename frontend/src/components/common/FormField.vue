<template>
  <div class="form-field" :class="[`type-${type}`, { 'has-error': !!error, 'is-required': required }]">
    <label v-if="label" :for="id" class="field-label">
      {{ label }}
      <span v-if="required" class="required-indicator">*</span>
    </label>
    
    <div class="field-content">
      <!-- Input de texto, email, password, number, tel -->
      <div v-if="['text', 'email', 'password', 'number', 'tel'].includes(type)" class="input-wrapper">
        <span v-if="prefixIcon" class="input-icon prefix">
          <i :class="prefixIcon"></i>
        </span>
        
        <input
          :id="id"
          :type="type"
          :value="value"
          :placeholder="placeholder"
          :disabled="disabled"
          :readonly="readonly"
          :min="min"
          :max="max"
          :step="step"
          :maxlength="maxlength"
          :autocomplete="autocomplete"
          class="form-input"
          @input="onInput"
          @blur="onBlur"
          @focus="onFocus"
        />
        
        <span v-if="suffixIcon" class="input-icon suffix">
          <i :class="suffixIcon"></i>
        </span>
        
        <div v-if="clearable && value && !disabled && !readonly" 
             class="clear-button" 
             @click="onClear">
          <i class="fas fa-times-circle"></i>
        </div>
      </div>
      
      <!-- Área de texto -->
      <textarea
        v-else-if="type === 'textarea'"
        :id="id"
        :value="value"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        :rows="rows"
        :maxlength="maxlength"
        class="form-textarea"
        @input="onInput"
        @blur="onBlur"
        @focus="onFocus"
      ></textarea>
      
      <!-- Select -->
      <div v-else-if="type === 'select'" class="select-wrapper">
        <select
          :id="id"
          :value="value"
          :disabled="disabled"
          class="form-select"
          @change="onChange"
          @blur="onBlur"
          @focus="onFocus"
        >
          <option v-if="placeholder" value="" disabled>{{ placeholder }}</option>
          <option
            v-for="option in options"
            :key="getOptionValue(option)"
            :value="getOptionValue(option)"
            :disabled="option.disabled"
          >
            {{ getOptionLabel(option) }}
          </option>
        </select>
        
        <span class="select-arrow">
          <i class="fas fa-chevron-down"></i>
        </span>
      </div>
      
      <!-- Checkbox -->
      <div v-else-if="type === 'checkbox'" class="checkbox-wrapper">
        <input
          :id="id"
          type="checkbox"
          :checked="value"
          :disabled="disabled"
          class="form-checkbox"
          @change="onCheckboxChange"
        />
        <label :for="id" class="checkbox-label">
          <slot name="checkbox-label">{{ checkboxLabel }}</slot>
        </label>
      </div>
      
      <!-- Radio buttons -->
      <div v-else-if="type === 'radio'" class="radio-group">
        <div
          v-for="option in options"
          :key="getOptionValue(option)"
          class="radio-option"
        >
          <input
            :id="`${id}-${getOptionValue(option)}`"
            type="radio"
            :name="id"
            :value="getOptionValue(option)"
            :checked="value === getOptionValue(option)"
            :disabled="disabled || option.disabled"
            class="form-radio"
            @change="onRadioChange($event, option)"
          />
          <label :for="`${id}-${getOptionValue(option)}`" class="radio-label">
            {{ getOptionLabel(option) }}
          </label>
        </div>
      </div>
      
      <!-- Date picker -->
      <div v-else-if="type === 'date'" class="date-wrapper">
        <span class="input-icon prefix">
          <i class="fas fa-calendar-alt"></i>
        </span>
        
        <input
          :id="id"
          type="date"
          :value="value"
          :min="min"
          :max="max"
          :disabled="disabled"
          :readonly="readonly"
          class="form-input form-date"
          @input="onInput"
          @blur="onBlur"
          @focus="onFocus"
        />
      </div>
      
      <!-- Time picker -->
      <div v-else-if="type === 'time'" class="time-wrapper">
        <span class="input-icon prefix">
          <i class="fas fa-clock"></i>
        </span>
        
        <input
          :id="id"
          type="time"
          :value="value"
          :min="min"
          :max="max"
          :disabled="disabled"
          :readonly="readonly"
          class="form-input form-time"
          @input="onInput"
          @blur="onBlur"
          @focus="onFocus"
        />
      </div>
      
      <!-- Switch toggle -->
      <div v-else-if="type === 'switch'" class="switch-wrapper">
        <label :for="id" class="switch-toggle">
          <input
            :id="id"
            type="checkbox"
            :checked="value"
            :disabled="disabled"
            @change="onCheckboxChange"
          />
          <span class="switch-slider"></span>
        </label>
        <label v-if="checkboxLabel" :for="id" class="switch-label">
          {{ checkboxLabel }}
        </label>
      </div>
    </div>
    
    <!-- Mensaje de ayuda o error -->
    <div v-if="error || helpText" class="field-message">
      <p v-if="error" class="error-message">
        <i class="fas fa-exclamation-circle"></i> {{ error }}
      </p>
      <p v-else-if="helpText" class="help-text">{{ helpText }}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FormField',
  props: {
    // Propiedades básicas
    id: {
      type: String,
      required: true
    },
    label: {
      type: String,
      default: ''
    },
    type: {
      type: String,
      default: 'text',
      validator: (value) => [
        'text', 'email', 'password', 'number', 'tel',
        'textarea', 'select', 'checkbox', 'radio',
        'date', 'time', 'switch'
      ].includes(value)
    },
    value: {
      type: [String, Number, Boolean, Array, Object],
      default: null
    },
    placeholder: {
      type: String,
      default: ''
    },
    helpText: {
      type: String,
      default: ''
    },
    error: {
      type: String,
      default: ''
    },
    
    // Estados
    disabled: {
      type: Boolean,
      default: false
    },
    readonly: {
      type: Boolean,
      default: false
    },
    required: {
      type: Boolean,
      default: false
    },
    
    // Opciones para select y radio
    options: {
      type: Array,
      default: () => []
      // Formato esperado: 
      // [{ value: 'value', label: 'Label', disabled: false }] 
      // o ['opcion1', 'opcion2', 'opcion3']
    },
    optionValue: {
      type: String,
      default: 'value'
    },
    optionLabel: {
      type: String,
      default: 'label'
    },
    
    // Para checkbox y switch
    checkboxLabel: {
      type: String,
      default: ''
    },
    
    // Para inputs numéricos y fechas
    min: {
      type: [Number, String],
      default: null
    },
    max: {
      type: [Number, String],
      default: null
    },
    step: {
      type: [Number, String],
      default: null
    },
    
    // Para texto y textareas
    maxlength: {
      type: Number,
      default: null
    },
    rows: {
      type: Number,
      default: 3
    },
    
    // Iconos
    prefixIcon: {
      type: String,
      default: ''
    },
    suffixIcon: {
      type: String,
      default: ''
    },
    
    // Otras opciones
    clearable: {
      type: Boolean,
      default: false
    },
    autocomplete: {
      type: String,
      default: 'off'
    }
  },
  methods: {
    onInput(event) {
      this.$emit('input', event.target.value);
    },
    onChange(event) {
      this.$emit('input', event.target.value);
      this.$emit('change', event.target.value);
    },
    onBlur(event) {
      this.$emit('blur', event);
    },
    onFocus(event) {
      this.$emit('focus', event);
    },
    onClear() {
      this.$emit('input', '');
      this.$emit('clear');
    },
    onCheckboxChange(event) {
      this.$emit('input', event.target.checked);
      this.$emit('change', event.target.checked);
    },
    onRadioChange(event, option) {
      const value = event.target.value;
      this.$emit('input', value);
      this.$emit('change', value, option);
    },
    // Manejar diferentes formatos de opciones
    getOptionValue(option) {
      if (typeof option !== 'object') return option;
      return option[this.optionValue] !== undefined ? option[this.optionValue] : option;
    },
    getOptionLabel(option) {
      if (typeof option !== 'object') return option;
      return option[this.optionLabel] !== undefined ? option[this.optionLabel] : option;
    }
  }
};
</script>

<style scoped>
.form-field {
  margin-bottom: 20px;
  width: 100%;
}

.field-label {
  display: block;
  margin-bottom: 6px;
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.required-indicator {
  color: #e53935;
  margin-left: 2px;
}

.field-content {
  position: relative;
}

/* Estilos para input de texto */
.form-input,
.form-textarea,
.form-select {
  width: 100%;
  padding: 10px 12px;
  font-size: 14px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #fff;
  color: #333;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-input:focus,
.form-textarea:focus,
.form-select:focus {
  border-color: #512da8;
  outline: none;
  box-shadow: 0 0 0 3px rgba(81, 45, 168, 0.1);
}

.input-wrapper {
  position: relative;
}

.input-icon {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  width: 36px;
  pointer-events: none;
}

.input-icon.prefix {
  left: 0;
}

.input-icon.suffix {
  right: 0;
}

.input-wrapper .form-input {
  padding-right: 30px;
}

.input-wrapper .form-input.has-prefix-icon {
  padding-left: 36px;
}

.input-wrapper .form-input.has-suffix-icon {
  padding-right: 36px;
}

/* Estilos para textarea */
.form-textarea {
  min-height: 100px;
  resize: vertical;
}

/* Estilos para select */
.select-wrapper {
  position: relative;
}

.form-select {
  appearance: none;
  padding-right: 30px;
}

.select-arrow {
  position: absolute;
  top: 50%;
  right: 12px;
  transform: translateY(-50%);
  pointer-events: none;
  color: #666;
}

/* Estilos para checkbox */
.checkbox-wrapper {
  display: flex;
  align-items: center;
}

.form-checkbox {
  position: absolute;
  opacity: 0;
}

.checkbox-label {
  position: relative;
  padding-left: 28px;
  cursor: pointer;
  font-size: 14px;
  user-select: none;
}

.checkbox-label:before {
  content: '';
  position: absolute;
  left: 0;
  top: 1px;
  width: 18px;
  height: 18px;
  border: 1px solid #ddd;
  border-radius: 3px;
  background-color: #fff;
  transition: all 0.2s;
}

.checkbox-label:after {
  content: '\f00c';
  font-family: 'Font Awesome 5 Free';
  font-weight: 900;
  position: absolute;
  left: 4px;
  top: 1px;
  font-size: 12px;
  color: #fff;
  opacity: 0;
  transition: opacity 0.2s;
}

.form-checkbox:checked + .checkbox-label:before {
  background-color: #512da8;
  border-color: #512da8;
}

.form-checkbox:checked + .checkbox-label:after {
  opacity: 1;
}

.form-checkbox:disabled + .checkbox-label {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Estilos para radio buttons */
.radio-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.radio-option {
  display: flex;
  align-items: center;
}

.form-radio {
  position: absolute;
  opacity: 0;
}

.radio-label {
  position: relative;
  padding-left: 28px;
  cursor: pointer;
  font-size: 14px;
  user-select: none;
}

.radio-label:before {
  content: '';
  position: absolute;
  left: 0;
  top: 1px;
  width: 18px;
  height: 18px;
  border: 1px solid #ddd;
  border-radius: 50%;
  background-color: #fff;
  transition: all 0.2s;
}

.radio-label:after {
  content: '';
  position: absolute;
  top: 5px;
  left: 4px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: #512da8;
  opacity: 0;
  transition: opacity 0.2s;
}

.form-radio:checked + .radio-label:before {
  border-color: #512da8;
}

.form-radio:checked + .radio-label:after {
  opacity: 1;
}

.form-radio:disabled + .radio-label {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Estilos para switch */
.switch-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
}

.switch-toggle {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 22px;
  margin: 0;
}

.switch-toggle input {
  opacity: 0;
  width: 0;
  height: 0;
}

.switch-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ddd;
  transition: .4s;
  border-radius: 22px;
}

.switch-slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 2px;
  bottom: 2px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

.switch-toggle input:checked + .switch-slider {
  background-color: #512da8;
}

.switch-toggle input:focus + .switch-slider {
  box-shadow: 0 0 1px #512da8;
}

.switch-toggle input:checked + .switch-slider:before {
  transform: translateX(22px);
}

.switch-toggle input:disabled + .switch-slider {
  opacity: 0.6;
  cursor: not-allowed;
}

.switch-label {
  font-size: 14px;
}

/* Estilos para date y time */
.date-wrapper,
.time-wrapper {
  position: relative;
}

.form-date,
.form-time {
  padding-left: 36px;
}

/* Botón para limpiar el campo */
.clear-button {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: #999;
  cursor: pointer;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: center;
}

.clear-button:hover {
  color: #666;
}

.form-input.has-suffix-icon + .clear-button {
  right: 36px;
}

/* Mensaje de error y ayuda */
.field-message {
  margin-top: 6px;
}

.error-message {
  color: #e53935;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
  margin: 0;
}

.help-text {
  font-size: 12px;
  color: #666;
  margin: 0;
}

/* Estados */
.has-error .form-input,
.has-error .form-textarea,
.has-error .form-select {
  border-color: #e53935;
}

.has-error .form-input:focus,
.has-error .form-textarea:focus,
.has-error .form-select:focus {
  box-shadow: 0 0 0 3px rgba(229, 57, 53, 0.1);
}

:disabled {
  cursor: not-allowed;
  opacity: 0.6;
  background-color: #f9f9f9;
}

[readonly] {
  background-color: #f9f9f9;
  cursor: default;
}
</style> 