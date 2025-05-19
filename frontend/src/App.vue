<template>
  <div id="app">
    <div v-if="appError" class="global-error">
      <div class="error-content">
        <h2>Error en la aplicación</h2>
        <p>{{ appError }}</p>
        <button @click="reloadApp" class="reload-button">Recargar aplicación</button>
      </div>
    </div>
    <div v-else>
      <Notification 
        :show="notification.show" 
        :message="notification.message" 
        :type="notification.type" 
        @close="clearNotification" 
      />
      <router-view />
    </div>
  </div>
</template>

<script>
import Notification from '@/components/common/Notification.vue';
import eventBus from '@/utils/eventBus';

export default {
  name: 'App',
  components: {
    Notification
  },
  data() {
    return {
      appError: null
    }
  },
  computed: {
    notification() {
      return this.$store.state.notification;
    }
  },
  mounted() {
    // Verificar si hay un token de sesión al iniciar la aplicación
    const token = localStorage.getItem('access_token');
    
    try {
      if (token) {
        this.$store.dispatch('auth/checkAuthStatus')
          .catch(error => {
            console.error('Error al verificar estado de autenticación:', error);
            // Si hay error de autenticación, redirigir al login
            if (this.$route.meta.requiresAuth) {
              this.$router.push('/login');
            }
          });
      }
    } catch (error) {
      console.error('Error crítico en la inicialización de la app:', error);
      this.appError = 'Ha ocurrido un error al iniciar la aplicación. Por favor recargue la página.';
    }
    
    // Configurar el eventBus para notificaciones en tiempo real
    eventBus.on('notification', this.showNotification);
    
    // Capturar errores no manejados
    window.addEventListener('error', this.handleGlobalError);
    window.addEventListener('unhandledrejection', this.handlePromiseRejection);
  },
  beforeUnmount() {
    window.removeEventListener('error', this.handleGlobalError);
    window.removeEventListener('unhandledrejection', this.handlePromiseRejection);
    eventBus.off('notification', this.showNotification);
  },
  methods: {
    handleGlobalError(event) {
      console.error('Error global capturado:', event.error);
      this.appError = 'Ha ocurrido un error inesperado en la aplicación.';
    },
    handlePromiseRejection(event) {
      console.error('Promesa rechazada no manejada:', event.reason);
      // Solo mostrar error si es crítico para la aplicación
      if (event.reason && event.reason.isCritical) {
        this.appError = 'Error de comunicación con el servidor.';
      }
    },
    reloadApp() {
      window.location.reload();
    },
    showNotification(notification) {
      this.$store.dispatch('showNotification', notification);
    },
    clearNotification() {
      this.$store.commit('CLEAR_NOTIFICATION');
    }
  }
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  background-color: #f4f7fa;
  margin: 0;
}

.global-error {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  width: 100%;
  background-color: #f8f9fa;
}

.error-content {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  padding: 30px;
  text-align: center;
  max-width: 500px;
}

.error-content h2 {
  color: #e74c3c;
  margin-bottom: 15px;
}

.error-content p {
  margin-bottom: 20px;
  color: #555;
}

.reload-button {
  background-color: #3a86ff;
  border: none;
  border-radius: 4px;
  color: white;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  padding: 10px 20px;
  transition: background-color 0.3s;
}

.reload-button:hover {
  background-color: #1a56cc;
}
</style>