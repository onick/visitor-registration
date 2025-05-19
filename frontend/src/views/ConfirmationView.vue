<template>
  <div class="confirmation-view">
    <div class="confirmation-content">
      <div class="success-icon">
        <i class="fas fa-check-circle"></i>
      </div>
      
      <h1>¡Registro Completado!</h1>
      <p class="confirmation-message">
        Gracias por registrarse para el evento. Su información ha sido guardada correctamente.
      </p>
      
      <div class="visitor-info">
        <h2>Información del Registro</h2>
        <div class="info-row">
          <span class="info-label">Nombre:</span>
          <span class="info-value">{{ visitorName }}</span>
        </div>
        <div class="info-row">
          <span class="info-label">Evento:</span>
          <span class="info-value">{{ eventName }}</span>
        </div>
        <div class="info-row">
          <span class="info-label">Código de Registro:</span>
          <span class="info-value confirmation-code">{{ registrationCode || confirmationCode }}</span>
        </div>
      </div>
      
      <div v-if="qrCode" class="qr-section">
        <h2>Código QR</h2>
        <p>Muestre este código al llegar al evento para un check-in más rápido.</p>
        <div class="qr-container" ref="qrContainer"></div>
      </div>
      
      <div v-if="loading" class="loading-message">
        <i class="fas fa-spinner fa-spin"></i>
        <p>Cargando información del evento...</p>
      </div>
      
      <div class="confirmation-actions">
        <button class="btn-primary" @click="returnToHome">
          Volver al Inicio
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import QRCode from 'qrcode';

export default {
  name: 'ConfirmationView',
  data() {
    return {
      visitorName: '',
      eventName: '',
      eventId: null,
      confirmationCode: '',
      registrationCode: '',
      qrCode: null,
      loading: false
    };
  },
  created() {
    // Obtener datos de múltiples fuentes posibles
    this.extractDataFromRoute();
    
    // Generar código de confirmación
    this.generateConfirmationCode();
  },
  mounted() {
    // Generar QR cuando el componente esté montado
    this.$nextTick(() => {
      this.generateQR();
    });
  },
  methods: {
    extractDataFromRoute() {
      // 1. Intentar obtener de params
      if (this.$route.params.visitorName) {
        this.visitorName = this.$route.params.visitorName;
      }
      
      if (this.$route.params.eventId) {
        this.eventId = this.$route.params.eventId;
      }
      
      if (this.$route.params.registrationCode) {
        this.registrationCode = this.$route.params.registrationCode;
      }
      
      // 2. Si no hay datos en params, intentar con query
      if (!this.visitorName && this.$route.query.visitorName) {
        this.visitorName = this.$route.query.visitorName;
      }
      
      if (!this.eventId && this.$route.query.eventId) {
        this.eventId = this.$route.query.eventId;
      }
      
      if (!this.registrationCode && this.$route.query.registrationCode) {
        this.registrationCode = this.$route.query.registrationCode;
      }
      
      // 3. Si no hay datos, intentar obtener del state/localStorage
      if (!this.visitorName || !this.eventId || !this.registrationCode) {
        const registrationData = localStorage.getItem('lastRegistration');
        if (registrationData) {
          try {
            const data = JSON.parse(registrationData);
            if (!this.visitorName) this.visitorName = data.visitorName;
            if (!this.eventId) this.eventId = data.eventId;
            if (!this.registrationCode) this.registrationCode = data.registrationCode;
          } catch (e) {
            console.error('Error parsing registration data:', e);
          }
        }
      }
      
      // 4. Cargar detalles del evento si tenemos eventId
      if (this.eventId) {
        this.loadEventDetails();
      }
    },
    
    async loadEventDetails() {
      if (!this.eventId) return;
      
      this.loading = true;
      try {
        // Intentar obtener detalles del evento desde el store
        let event = await this.$store.dispatch('events/fetchEventById', this.eventId);
        
        if (!event) {
          // Si no está en el store, intentar obtener de los eventos cargados
          const allEvents = this.$store.getters['events/allEvents'];
          event = allEvents.find(e => e.id == this.eventId);
        }
        
        if (event) {
          this.eventName = event.title || event.name;
        } else {
          // Fallback por si no encontramos el evento
          this.eventName = 'Evento del Centro Cultural';
        }
      } catch (error) {
        console.error('Error al cargar detalles del evento:', error);
        this.eventName = 'Evento CCB';
      } finally {
        this.loading = false;
      }
    },
    
    generateConfirmationCode() {
      // Generar un código alfanumérico aleatorio
      const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
      let code = '';
      for (let i = 0; i < 8; i++) {
        code += chars.charAt(Math.floor(Math.random() * chars.length));
      }
      this.confirmationCode = code;
    },
    
    generateQR() {
      // Verificar si la referencia al contenedor existe
      if (!this.$refs.qrContainer) {
        console.warn('Contenedor QR no encontrado');
        this.qrCode = false;
        return;
      }
      
      try {
        const data = JSON.stringify({
          registrationCode: this.registrationCode || this.confirmationCode,
          eventId: this.eventId,
          visitorName: this.visitorName
        });
        
        // Envolver en try-catch y usar async/await para mejor manejo de errores
        QRCode.toCanvas(this.$refs.qrContainer, data, {
          width: 200,
          margin: 2,
          color: {
            dark: '#474C55',
            light: '#ffffff'
          }
        }).then(() => {
          this.qrCode = true;
        }).catch(err => {
          console.error('Error al generar QR:', err);
          this.qrCode = false;
        });
      } catch (err) {
        console.error('Error al intentar generar QR:', err);
        this.qrCode = false;
      }
    },
    
    returnToHome() {
      // Limpiar datos temporales
      localStorage.removeItem('lastRegistration');
      this.$router.push('/kiosk/idle');
    }
  }
};
</script>

<style scoped>
.confirmation-view {
  min-height: 100vh;
  background-color: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.confirmation-content {
  max-width: 600px;
  width: 100%;
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  padding: 40px;
  text-align: center;
}

.success-icon {
  font-size: 5rem;
  color: #43a047;
  margin-bottom: 20px;
}

h1 {
  color: #333;
  margin-bottom: 15px;
}

.confirmation-message {
  color: #666;
  font-size: 1.2rem;
  margin-bottom: 30px;
}

.visitor-info {
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 30px;
  text-align: left;
}

.visitor-info h2 {
  font-size: 1.3rem;
  color: #333;
  margin-bottom: 15px;
  text-align: center;
}

.info-row {
  display: flex;
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.info-row:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.info-label {
  font-weight: 500;
  color: #666;
  width: 100px;
}

.info-value {
  flex: 1;
  color: #333;
}

.confirmation-code {
  font-weight: 700;
  font-size: 1.2rem;
  color: var(--color-primary);
  letter-spacing: 1px;
}

.qr-section {
  margin-bottom: 30px;
}

.qr-section h2 {
  font-size: 1.3rem;
  color: #333;
  margin-bottom: 10px;
}

.qr-section p {
  color: #666;
  margin-bottom: 15px;
}

.qr-container {
  display: flex;
  justify-content: center;
  margin: 20px 0;
}

.loading-message {
  text-align: center;
  color: #666;
  margin: 20px 0;
}

.loading-message i {
  font-size: 2rem;
  color: var(--color-primary);
  margin-bottom: 10px;
}

.confirmation-actions {
  margin-top: 30px;
}

.btn-primary {
  background-color: var(--color-primary);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-primary:hover {
  background-color: var(--color-primary-dark);
}

@media (max-width: 768px) {
  .confirmation-content {
    padding: 30px 20px;
  }
  
  .success-icon {
    font-size: 4rem;
  }
  
  h1 {
    font-size: 1.8rem;
  }
  
  .confirmation-message {
    font-size: 1rem;
  }
}
</style>
