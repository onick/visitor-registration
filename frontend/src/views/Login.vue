<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <img src="@/assets/images/logo.png" alt="Centro Cultural Banreservas" class="login-logo">
        <p class="login-subtitle">Sistema de Registro de Visitantes</p>
      </div>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group" :class="{ 'has-error': errors.email }">
          <label for="email">Nombre de Usuario</label>
          <div class="input-with-icon">
            <i class="fas fa-user"></i>
            <input 
              type="text" 
              id="email" 
              v-model="form.email" 
              placeholder="Ingrese su nombre de usuario"
              required
              @focus="clearError('email')"
            />
          </div>
          <p class="error-message" v-if="errors.email">{{ errors.email }}</p>
        </div>
        
        <div class="form-group" :class="{ 'has-error': errors.password }">
          <label for="password">Contraseña</label>
          <div class="input-with-icon">
            <i class="fas fa-lock"></i>
            <input 
              :type="showPassword ? 'text' : 'password'" 
              id="password" 
              v-model="form.password" 
              placeholder="Ingrese su contraseña"
              required
              @focus="clearError('password')"
            />
            <button 
              type="button" 
              class="toggle-password" 
              @click="togglePasswordVisibility"
            >
              <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
            </button>
          </div>
          <p class="error-message" v-if="errors.password">{{ errors.password }}</p>
        </div>
        
        <div class="form-options">
          <label class="remember-me">
            <input type="checkbox" v-model="form.rememberMe" />
            <span>Recordarme</span>
          </label>
          <router-link to="/forgot-password" class="forgot-password">
            ¿Olvidó su contraseña?
          </router-link>
        </div>
        
        <div class="form-actions">
          <button 
            type="submit" 
            class="login-button" 
            :disabled="isLoading"
          >
            <span v-if="!isLoading">Iniciar Sesión</span>
            <span v-else class="loading-spinner">
              <i class="fas fa-circle-notch fa-spin"></i>
            </span>
          </button>
        </div>
        
        <div class="alert alert-danger" v-if="generalError">
          {{ generalError }}
        </div>
      </form>
      
      <div class="login-footer">
        <p>¿No tiene una cuenta? Contacte al administrador</p>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex';

export default {
  name: 'Login',
  data() {
    return {
      form: {
        email: '',
        password: '',
        rememberMe: false
      },
      errors: {
        email: '',
        password: ''
      },
      generalError: '',
      isLoading: false,
      showPassword: false
    };
  },
  methods: {
    ...mapActions('auth', ['login']),
    
    async handleLogin() {
      // Reset errors
      this.errors = { email: '', password: '' };
      this.generalError = '';
      
      // Validate form
      let isValid = true;
      
      if (!this.form.email) {
        this.errors.email = 'El nombre de usuario es requerido';
        isValid = false;
      }
      
      if (!this.form.password) {
        this.errors.password = 'La contraseña es requerida';
        isValid = false;
      }
      
      if (!isValid) return;
      
      // Submit form
      this.isLoading = true;
      
      try {
        await this.login({
          email: this.form.email,
          password: this.form.password,
          remember: this.form.rememberMe
        });
        
        // Redirect to dashboard or previous page
        const redirectPath = this.$route.query.redirect || '/admin/dashboard';
        this.$router.push(redirectPath);
      } catch (error) {
        if (error.response && error.response.status === 401) {
          this.generalError = 'Credenciales inválidas. Por favor, verifique su nombre de usuario y contraseña.';
        } else if (error.response && error.response.data && error.response.data.message) {
          this.generalError = error.response.data.message;
        } else {
          this.generalError = 'Ha ocurrido un error. Por favor, intente nuevamente.';
        }
      } finally {
        this.isLoading = false;
      }
    },
    
    clearError(field) {
      this.errors[field] = '';
      this.generalError = '';
    },
    
    togglePasswordVisibility() {
      this.showPassword = !this.showPassword;
    }
  }
};
</script>

<style scoped>
.login-container {
  align-items: center;
  background: linear-gradient(135deg, #3a86ff 0%, #1a56cc 100%);
  display: flex;
  height: 100vh;
  justify-content: center;
  width: 100%;
}

.login-card {
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  max-width: 450px;
  padding: 40px;
  width: 100%;
}

.login-header {
  margin-bottom: 30px;
  text-align: center;
}

.login-logo {
  width: 150px;
  height: auto;
  margin-bottom: 15px;
}

.login-subtitle {
  color: #666;
  font-size: 16px;
  margin: 0;
}

.login-form {
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

.form-options {
  align-items: center;
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.remember-me {
  align-items: center;
  cursor: pointer;
  display: flex;
  font-size: 14px;
}

.remember-me input {
  margin-right: 8px;
}

.forgot-password {
  color: #3a86ff;
  font-size: 14px;
  text-decoration: none;
}

.forgot-password:hover {
  text-decoration: underline;
}

.form-actions {
  margin-bottom: 20px;
}

.login-button {
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

.login-button:hover {
  background-color: #1a56cc;
}

.login-button:disabled {
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

.login-footer {
  color: #666;
  font-size: 14px;
  text-align: center;
}

@media (max-width: 500px) {
  .login-card {
    border-radius: 0;
    box-shadow: none;
    height: 100vh;
    max-width: none;
    padding: 30px 20px;
  }
  
  .login-container {
    padding: 0;
  }
}
</style>