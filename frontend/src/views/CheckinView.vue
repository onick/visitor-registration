<template>
  <div class="checkin-view">
    <kiosk-header title="Check-in de Visitantes" :showBackButton="true" @back="goBack" />
    
    <div class="checkin-container">
      <div v-if="step === 'scan'" class="scan-section">
        <h2>Escanee su código QR</h2>
        <div class="qr-scanner-container">
          <div class="qr-scanner-placeholder">
            <!-- Aquí iría el componente de escaneo de QR real -->
            <div class="scanner-animation"></div>
          </div>
        </div>
        <p class="instruction">Coloque el código QR de su confirmación frente a la cámara</p>
        <div class="alternative-options">
          <button class="btn btn-secondary" @click="step = 'manual'">
            Ingresar código manualmente
          </button>
        </div>
      </div>

      <div v-else-if="step === 'manual'" class="manual-section">
        <h2>Ingrese su código de confirmación</h2>
        <div class="form-group">
          <label for="confirmation-code">Código de confirmación</label>
          <input 
            type="text" 
            id="confirmation-code" 
            v-model="confirmationCode" 
            placeholder="Ej. ABC123"
            class="form-control"
          />
        </div>
        <div class="action-buttons">
          <button class="btn btn-secondary" @click="step = 'scan'">
            Volver al escáner
          </button>
          <button class="btn btn-primary" @click="verifyCode" :disabled="!confirmationCode">
            Verificar
          </button>
        </div>
      </div>

      <div v-else-if="step === 'success'" class="success-section">
        <div class="success-icon">
          <i class="fas fa-check-circle"></i>
        </div>
        <h2>¡Bienvenido/a!</h2>
        <div class="visitor-info">
          <h3>{{ visitor.name }}</h3>
          <p class="event-name">{{ event.title }}</p>
          <p class="timestamp">Check-in: {{ formatDate(new Date()) }}</p>
        </div>
        <button class="btn btn-primary mt-4" @click="finishCheckin">
          Continuar
        </button>
      </div>

      <div v-else-if="step === 'error'" class="error-section">
        <div class="error-icon">
          <i class="fas fa-times-circle"></i>
        </div>
        <h2>No se pudo completar el check-in</h2>
        <p>{{ errorMessage }}</p>
        <div class="action-buttons">
          <button class="btn btn-secondary" @click="step = 'scan'">
            Intentar nuevamente
          </button>
          <button class="btn btn-primary" @click="goBack">
            Volver al inicio
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import KioskHeader from '@/components/kiosk/KioskHeader.vue';
import { mapActions } from 'vuex';

export default {
  name: 'CheckinView',
  components: {
    KioskHeader
  },
  data() {
    return {
      step: 'scan', // 'scan', 'manual', 'success', 'error'
      confirmationCode: '',
      visitor: null,
      event: null,
      errorMessage: '',
      inactivityTimer: null
    };
  },
  mounted() {
    this.startInactivityTimer();
    // Simulación de escaneo para desarrollo
    // En producción, esto sería reemplazado por un componente real de escaneo
    if (process.env.NODE_ENV === 'development') {
      window.addEventListener('keydown', this.handleDevScanSimulation);
    }
  },
  beforeUnmount() {
    if (this.scannerInterval) {
      clearInterval(this.scannerInterval);
    }
  },
  methods: {
    ...mapActions({
      checkInVisitor: 'visitors/checkInVisitor',
      getVisitorByCode: 'visitors/getVisitorByCode',
      getEventById: 'events/getEventById'
    }),
    startInactivityTimer() {
      clearTimeout(this.inactivityTimer);
      this.inactivityTimer = setTimeout(() => {
        this.goBack();
      }, 120000); // 2 minutos de inactividad
    },
    resetInactivityTimer() {
      this.startInactivityTimer();
    },
    handleDevScanSimulation(e) {
      // Simulación para desarrollo: presionar 'S' simula un escaneo exitoso
      if (e.key === 's' || e.key === 'S') {
        this.simulateSuccessfulScan();
      }
    },
    simulateSuccessfulScan() {
      // Datos de ejemplo para desarrollo
      this.visitor = {
        id: 'v123',
        firstName: 'Juan',
        lastName: 'Pérez',
        email: 'juan@ejemplo.com'
      };
      this.event = {
        id: 'e456',
        title: 'Exposición de Arte Contemporáneo',
        date: new Date()
      };
      this.step = 'success';
      this.resetInactivityTimer();
    },
    async verifyCode() {
      this.resetInactivityTimer();
      if (!this.confirmationCode) return;
      
      try {
        // Llamar a la API para verificar el código
        const response = await this.getVisitorByCode(this.confirmationCode);
        
        if (response && response.visitor) {
          this.visitor = response.visitor;
          
          // Si hay eventos disponibles, usar el primero
          if (response.events && response.events.length > 0) {
            // En un escenario real, si hay múltiples eventos, se debería preguntar al usuario
            const eventData = response.events[0];
            this.event = {
              id: eventData.id,
              title: eventData.title,
              location: eventData.location,
              start_date: eventData.start_date,
              end_date: eventData.end_date
            };
            
            // Registrar el check-in
            await this.checkInVisitor({
              visitorId: this.visitor.id,
              eventId: this.event.id
            });
            
            this.step = 'success';
          } else {
            this.step = 'error';
            this.errorMessage = 'No hay eventos disponibles para este código.';
          }
        } else {
          this.step = 'error';
          this.errorMessage = 'Código de confirmación no válido. Por favor, verifique e intente nuevamente.';
        }
      } catch (error) {
        this.step = 'error';
        this.errorMessage = error.response?.data?.error || 'Ha ocurrido un error al verificar su código. Por favor, intente nuevamente.';
        console.error('Error al verificar código:', error);
      }
    },
    formatDate(date) {
      return new Intl.DateTimeFormat('es-ES', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }).format(date);
    },
    finishCheckin() {
      this.resetInactivityTimer();
      this.step = 'scan';
      this.confirmationCode = '';
      this.visitor = null;
      this.event = null;
    },
    goBack() {
      this.$router.push('/kiosk/welcome');
    }
  }
};
</script>

<style scoped>
.checkin-view {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f8f9fa;
}

.checkin-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.scan-section, .manual-section, .success-section, .error-section {
  width: 100%;
  max-width: 600px;
  text-align: center;
}

h2 {
  margin-bottom: 2rem;
  color: #333;
  font-size: 2rem;
}

.qr-scanner-container {
  width: 300px;
  height: 300px;
  margin: 0 auto 2rem;
  border: 3px solid #007bff;
  border-radius: 10px;
  overflow: hidden;
  position: relative;
}

.qr-scanner-placeholder {
  width: 100%;
  height: 100%;
  background-color: rgba(0, 123, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
}

.scanner-animation {
  width: 100%;
  height: 2px;
  background-color: red;
  position: absolute;
  animation: scan 2s infinite ease-in-out;
}

@keyframes scan {
  0% { top: 0; }
  50% { top: 100%; }
  100% { top: 0; }
}

.instruction {
  font-size: 1.2rem;
  margin-bottom: 2rem;
  color: #666;
}

.alternative-options {
  margin-top: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
  width: 100%;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
  text-align: left;
}

.form-control {
  width: 100%;
  padding: 0.75rem;
  font-size: 1.1rem;
  border: 1px solid #ced4da;
  border-radius: 0.25rem;
}

.action-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 2rem;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

.success-icon, .error-icon {
  font-size: 5rem;
  margin-bottom: 1.5rem;
}

.success-icon {
  color: #28a745;
}

.error-icon {
  color: #dc3545;
}

.visitor-info {
  background-color: #fff;
  padding: 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin: 2rem 0;
}

.visitor-info h3 {
  font-size: 1.8rem;
  margin-bottom: 0.5rem;
}

.event-name {
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
  color: #495057;
}

.timestamp {
  font-size: 1rem;
  color: #6c757d;
}

.btn {
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background-color: #007bff;
  color: white;
  border: none;
}

.btn-primary:hover {
  background-color: #0069d9;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
  border: none;
}

.btn-secondary:hover {
  background-color: #5a6268;
}

.btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.mt-4 {
  margin-top: 2rem;
}

/* Estilos responsivos */
@media (max-width: 768px) {
  .qr-scanner-container {
    width: 250px;
    height: 250px;
  }
  
  h2 {
    font-size: 1.5rem;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 1rem;
  }
}
</style> 