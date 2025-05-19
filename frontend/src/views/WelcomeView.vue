<template>
  <div class="welcome-view">
    <div class="welcome-content">
      <div class="logo-container">
        <div class="logo-placeholder">
          <div class="logo-text">CCB</div>
        </div>
      </div>
      
      <h1>¡Bienvenido al Centro Cultural Banreservas!</h1>
      <p>Por favor seleccione una opción:</p>
      
      <div class="options">
        <div class="option-card" @click="goToEvents">
          <div class="option-icon">
            <i class="fas fa-calendar-alt"></i>
          </div>
          <h2>Ver Eventos</h2>
          <p>Explore nuestros eventos actuales y próximos</p>
        </div>
        
        <div class="option-card" @click="goToRegister">
          <div class="option-icon">
            <i class="fas fa-user-plus"></i>
          </div>
          <h2>Registrarse</h2>
          <p>Regístrese para un evento específico</p>
        </div>
        
        <div class="option-card" @click="goToCheckin">
          <div class="option-icon">
            <i class="fas fa-check-circle"></i>
          </div>
          <h2>Check-in</h2>
          <p>Confirme su asistencia a un evento</p>
        </div>
      </div>
      
      <div class="admin-link">
        <button class="btn-link" @click="goToAdmin">Acceso Administrativo</button>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex';

export default {
  name: 'WelcomeView',
  methods: {
    ...mapActions('auth', ['autoLogin']),
    goToEvents() {
      this.$router.push('/kiosk/events');
    },
    goToRegister() {
      this.$router.push('/kiosk/register');
    },
    goToCheckin() {
      this.$router.push('/kiosk/checkin');
    },
    async goToAdmin() {
      try {
        await this.autoLogin();
        this.$router.push('/admin/dashboard');
      } catch (error) {
        console.error('Error al iniciar sesión automática:', error);
        // Si falla el login automático, redirigir a la página de login normal
        this.$router.push('/login');
      }
    }
  }
};
</script>

<style scoped>
.welcome-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: linear-gradient(135deg, #f5f5f5, #e0e0e0);
}

.welcome-content {
  max-width: 1000px;
  width: 100%;
  text-align: center;
  padding: 40px;
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.logo-container {
  margin-bottom: 30px;
}

.logo-placeholder {
  width: 120px;
  height: 120px;
  background-color: #512da8;
  border-radius: 50%;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.logo-text {
  font-size: 2.5rem;
  font-weight: bold;
}

h1 {
  color: #333;
  margin-bottom: 15px;
}

p {
  color: #666;
  font-size: 1.2rem;
  margin-bottom: 40px;
}

.options {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-bottom: 50px;
  flex-wrap: wrap;
}

.option-card {
  background-color: white;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 30px;
  width: 280px;
  text-align: center;
  transition: all 0.3s ease;
  cursor: pointer;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
}

.option-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
  border-color: #512da8;
}

.option-icon {
  font-size: 3rem;
  color: #512da8;
  margin-bottom: 20px;
}

.option-card h2 {
  color: #333;
  font-size: 1.5rem;
  margin-bottom: 10px;
}

.option-card p {
  color: #666;
  font-size: 1rem;
  margin-bottom: 0;
}

.admin-link {
  margin-top: 30px;
}

.btn-link {
  background: none;
  border: none;
  color: #512da8;
  text-decoration: underline;
  font-size: 1rem;
  cursor: pointer;
  padding: 5px 10px;
}

.btn-link:hover {
  color: #140078;
}

@media (max-width: 768px) {
  .welcome-content {
    padding: 20px;
  }
  
  .options {
    flex-direction: column;
    align-items: center;
  }
  
  .option-card {
    width: 100%;
    max-width: 280px;
  }
}
</style> 