<template>
  <div class="reset-password-container">
    <div class="reset-password-card">
      <div class="reset-password-header">
        <div class="logo-text">CCB</div>
        <h1 class="reset-password-title">Restablecer Contraseña</h1>
        <p class="reset-password-subtitle">Ingrese su nueva contraseña</p>
      </div>
      
      <form @submit.prevent="handleSubmit" class="reset-password-form">
        <div class="form-group" :class="{ 'has-error': errors.password }">
          <label for="password">Nueva Contraseña</label>
          <div class="input-with-icon">
            <i class="fas fa-lock"></i>
            <input 
              :type="showPassword ? 'text' : 'password'" 
              id="password" 
              v-model="form.password" 
              placeholder="Ingrese su nueva contraseña"
              required
              @focus="clearError('password')"
            />
            <button 
              type="button" 
              class="toggle-password" 
              @click="togglePasswordVisibility('password')"
            >
              <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
            </button>
          </div>
          <p class="error-message" v-if="errors.password">{{ errors.password }}</p>
        </div>
        
        <div class="form-group" :class="{ 'has-error': errors.confirmPassword }">
          <label for="confirmPassword">Confirmar Contraseña</label>
          <div class="input-with-icon">
            <i class="fas fa-lock"></i>
            <input 
              :type="showConfirmPassword ? 'text' : 'password'" 
              id="confirmPassword" 
              v-model="form.confirmPassword" 
              placeholder="Confirme su nueva contraseña"
              required
              @focus="clearError('confirmPassword')"
            />
            <button 
              type="button" 
              class="toggle-password" 
              @click="togglePasswordVisibility('confirm')"
            >
              <i :class="showConfirmPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
            </button>
          </div>
          <p class="error-message" v-if="errors.confirmPassword">{{ errors.confirmPassword }}</p>
        </div>
        
        <div class="form-actions">
          <button 
            type="submit" 
            class="submit-button" 
            :disabled="isLoading"
          >
            <span v-if="!isLoading">Restablecer Contraseña</span>
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
      
      <div class="reset-password-footer">
        <p>¿Recordó su contraseña? <router-link to="/login">Volver al inicio de sesión</router-link></p>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex';

export default {
  name: 'ResetPasswordView',
  data() {
    return {
      form: {
        password: '',
        confirmPassword: ''
      },
      errors: {
        password: '',
        confirmPassword: ''
      },
      generalError: '',
      successMessage: '',
      isLoading: false,
      showPassword: false,
      showConfirmPassword: false,
      token: ''
    };
  },
  created() {
    // Get token from route params
    this.token = this.$route.params.token;
    
    // Validate token
    this.validateToken();
  },
  methods: {
    ...mapActions('auth', ['resetPassword', 'validateToken']),
    
    async validateToken() {
      this.isLoading = true;
      
      try {
        const isValid = await this.validateToken(this.token);
        
        if (!isValid) {
          this.generalError = 'El enlace de recuperación es inválido o ha expirado. Por favor, solicite uno nuevo.';
          setTimeout(() => {
            this.$router.push('/forgot-password');
          }, 3000);
        }
      } catch (error) {
        this.generalError = 'El enlace de recuperación es inválido o ha expirado. Por favor, solicite uno nuevo.';
        setTimeout(() => {
          this.$router.push('/forgot-password');
        }, 3000);
      } finally {
        this.isLoading = false;
      }
    },
    
    async handleSubmit() {
      // Reset errors and messages
      this.errors = { password: '', confirmPassword: '' };
      this.generalError = '';
      this.successMessage = '';
      
      // Validate form
      let isValid = true;
      
      if (!this.form.password) {
        this.errors.password = 'La contraseña es requerida';
        isValid = false;
      } else if (this.form.password.length < 8) {
        this.errors.password = 'La contraseña debe tener al menos 8 caracteres';
        isValid = false;
      }
      
      if (!this.form.confirmPassword) {
        this.errors.confirmPassword = 'Debe confirmar la contraseña';
        isValid = false;
      } else if (this.form.password !== this.form.confirmPassword) {
        this.errors.confirmPassword = 'Las contraseñas no coinciden';
        isValid = false;
      }
      
      if (!isValid) return;
      
      // Submit form
      this.isLoading = true;
      
      try {
        await this.resetPassword({
          token: this.token,
          password: this.form.password
        });
        
        // Show success message
        this.successMessage = 'Su contraseña ha sido restablecida exitosamente. Será redirigido al inicio de sesión.';
        
        // Clear the form
        this.form.password = '';
        this.form.confirmPassword = '';
        
        // Redirect to login after a delay
        setTimeout(() => {
          this.$router.push('/login');
        }, 3000);
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
    
    togglePasswordVisibility(field) {
      if (field === 'password') {
        this.showPassword = !this.showPassword;
      } else {
        this.showConfirmPassword = !this.showConfirmPassword;
      }
    },
    
    clearError(field) {
      this.errors[field] = '';
      this.generalError = '';
    }
  }
};
</script>

<style scoped>
.reset-password-container {
  align-items: center;
  background: linear-gradient(135deg, #3a86ff 0%, #1a56cc 100%);
  display: flex;
  height: 100vh;
  justify-content: center;
  width: 100%;
}

.reset-password-card {
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  max-width: 450px;
  padding: 40px;
  width: 100%;
}

.reset-password-header {
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

.reset-password-title {
  color: #333;
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 10px 0;
}

.reset-password-subtitle {
  color: #666;
  font-size: 16px;
  margin: 0;
}

.reset-password-form {
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

.toggle-password {
  background: none;
  border: none;
  color: #aaa;
  cursor: pointer;
  padding: 0;
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
}

.toggle-password:focus {
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

.reset-password-footer {
  color: #666;
  font-size: 14px;
  text-align: center;
}

.reset-password-footer a {
  color: #3a86ff;
  text-decoration: none;
}

.reset-password-footer a:hover {
  text-decoration: underline;
}

@media (max-width: 500px) {
  .reset-password-card {
    border-radius: 0;
    box-shadow: none;
    height: 100vh;
    max-width: none;
    padding: 30px 20px;
  }
  
  .reset-password-container {
    padding: 0;
  }
}
</style> 