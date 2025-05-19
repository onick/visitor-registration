<template>
  <div class="forgot-password-container">
    <div class="forgot-password-card">
      <div class="forgot-password-header">
        <div class="logo-text">CCB</div>
        <h1 class="forgot-password-title">Recuperar Contraseña</h1>
        <p class="forgot-password-subtitle">Ingrese su correo electrónico para recibir un enlace de recuperación</p>
      </div>
      
      <form @submit.prevent="handleSubmit" class="forgot-password-form">
        <div class="form-group" :class="{ 'has-error': errors.email }">
          <label for="email">Correo Electrónico</label>
          <div class="input-with-icon">
            <i class="fas fa-envelope"></i>
            <input 
              type="email" 
              id="email" 
              v-model="form.email" 
              placeholder="Ingrese su correo electrónico"
              required
              @focus="clearError('email')"
            />
          </div>
          <p class="error-message" v-if="errors.email">{{ errors.email }}</p>
        </div>
        
        <div class="form-actions">
          <button 
            type="submit" 
            class="submit-button" 
            :disabled="isLoading"
          >
            <span v-if="!isLoading">Enviar Enlace</span>
            <span v-else class="loading-spinner">
              <i class="fas fa-circle-notch fa-spin"></i>
            </span>
          </button>
        </div>
        
        <div class="alert alert-danger" v-if="generalError">
          {{ generalError }}
        </div>
        
        <div class="alert alert-success" v-if="successMessage">
          {{ successMessage }}
        </div>
      </form>
      
      <div class="forgot-password-footer">
        <p>¿Recordó su contraseña? <router-link to="/login">Volver al inicio de sesión</router-link></p>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex';

export default {
  name: 'ForgotPasswordView',
  data() {
    return {
      form: {
        email: ''
      },
      errors: {
        email: ''
      },
      generalError: '',
      successMessage: '',
      isLoading: false
    };
  },
  methods: {
    ...mapActions('auth', ['requestPasswordReset']),
    
    async handleSubmit() {
      // Reset errors and messages
      this.errors = { email: '' };
      this.generalError = '';
      this.successMessage = '';
      
      // Validate form
      let isValid = true;
      
      if (!this.form.email) {
        this.errors.email = 'El correo electrónico es requerido';
        isValid = false;
      } else if (!this.validateEmail(this.form.email)) {
        this.errors.email = 'Ingrese un correo electrónico válido';
        isValid = false;
      }
      
      if (!isValid) return;
      
      // Submit form
      this.isLoading = true;
      
      try {
        await this.requestPasswordReset(this.form.email);
        
        // Show success message
        this.successMessage = 'Se ha enviado un enlace de recuperación a su correo electrónico. Por favor, revise su bandeja de entrada.';
        this.form.email = ''; // Clear the form
      } catch (error) {
        if (error.response && error.response.data && error.response.data.message) {
          this.generalError = error.response.data.message;
        } else {
          this.generalError = 'Ha ocurrido un error. Por favor, intente nuevamente.';
        }
      } finally {
        this.isLoading = false;
      }
    },
    
    validateEmail(email) {
      const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return re.test(email);
    },
    
    clearError(field) {
      this.errors[field] = '';
      this.generalError = '';
    }
  }
};
</script>

<style scoped>
.forgot-password-container {
  align-items: center;
  background: linear-gradient(135deg, #3a86ff 0%, #1a56cc 100%);
  display: flex;
  height: 100vh;
  justify-content: center;
  width: 100%;
}

.forgot-password-card {
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  max-width: 450px;
  padding: 40px;
  width: 100%;
}

.forgot-password-header {
  margin-bottom: 30px;
  text-align: center;
}

.logo-text {
  background-color: #3a86ff;
  border-radius: 50%;
  color: white;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: bold;
  height: 70px;
  margin-bottom: 20px;
  width: 70px;
}

.forgot-password-title {
  color: #333;
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 10px 0;
}

.forgot-password-subtitle {
  color: #666;
  font-size: 16px;
  margin: 0;
}

.forgot-password-form {
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  color: #555;
  display: block;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 8px;
}

.input-with-icon {
  position: relative;
}

.input-with-icon i {
  color: #aaa;
  left: 12px;
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
}

.input-with-icon input {
  background-color: #f5f7fa;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  padding: 12px 12px 12px 40px;
  transition: border-color 0.3s, box-shadow 0.3s;
  width: 100%;
}

.input-with-icon input:focus {
  border-color: #3a86ff;
  box-shadow: 0 0 0 2px rgba(58, 134, 255, 0.2);
  outline: none;
}

.form-group.has-error input {
  border-color: #e74c3c;
}

.error-message {
  color: #e74c3c;
  font-size: 12px;
  margin: 5px 0 0 0;
}

.form-actions {
  margin-bottom: 20px;
}

.submit-button {
  background-color: #3a86ff;
  border: none;
  border-radius: 4px;
  color: white;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  padding: 12px;
  transition: background-color 0.3s;
  width: 100%;
}

.submit-button:hover {
  background-color: #1a56cc;
}

.submit-button:disabled {
  background-color: #a0c4ff;
  cursor: not-allowed;
}

.loading-spinner {
  display: inline-block;
}

.alert {
  border-radius: 4px;
  margin-top: 20px;
  padding: 12px;
}

.alert-danger {
  background-color: #fdecea;
  border: 1px solid #f5c6cb;
  color: #e74c3c;
}

.alert-success {
  background-color: #d4edda;
  border: 1px solid #c3e6cb;
  color: #155724;
}

.forgot-password-footer {
  color: #666;
  font-size: 14px;
  text-align: center;
}

.forgot-password-footer a {
  color: #3a86ff;
  text-decoration: none;
}

.forgot-password-footer a:hover {
  text-decoration: underline;
}

@media (max-width: 500px) {
  .forgot-password-card {
    border-radius: 0;
    box-shadow: none;
    height: 100vh;
    max-width: none;
    padding: 30px 20px;
  }
  
  .forgot-password-container {
    padding: 0;
  }
}
</style> 