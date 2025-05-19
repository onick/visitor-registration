<template>
  <div class="registration-view">
    <div class="registration-content">
      <div class="header">
        <button class="back-button" @click="goBack">
          <i class="fas fa-arrow-left"></i> Volver
        </button>
        <h1>Registro de Visitante</h1>
      </div>
      
      <div class="form-container">
        <div class="form-section">
          <h2>Información Personal</h2>
          
          <div class="form-row">
            <div class="form-group">
              <label for="firstName">Nombre *</label>
              <input 
                type="text" 
                id="firstName" 
                v-model="visitor.first_name" 
                placeholder="Ingrese su nombre"
                required
              >
            </div>
            
            <div class="form-group">
              <label for="lastName">Apellido *</label>
              <input 
                type="text" 
                id="lastName" 
                v-model="visitor.last_name" 
                placeholder="Ingrese su apellido"
                required
              >
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label for="email">Correo Electrónico *</label>
              <input 
                type="email" 
                id="email" 
                v-model="visitor.email" 
                placeholder="ejemplo@correo.com"
                required
              >
            </div>
            
            <div class="form-group">
              <label for="phone">Teléfono *</label>
              <input 
                type="tel" 
                id="phone" 
                v-model="visitor.phone" 
                placeholder="(XXX) XXX-XXXX"
                required
              >
            </div>
          </div>
          
          <div class="form-group">
            <label for="identification">Documento de Identidad</label>
            <input 
              type="text" 
              id="identification" 
              v-model="visitor.identification" 
              placeholder="Cédula o Pasaporte"
            >
          </div>
        </div>
        
        <div class="form-section">
          <h2>Seleccione un Evento</h2>
          
          <div class="event-title-highlight" v-if="selectedEvent">
            <h3>Evento seleccionado: 
              <span>{{ selectedEventName }}</span>
            </h3>
          </div>
          
          <div class="events-list">
            <div 
              v-for="event in events" 
              :key="event.id" 
              class="event-card"
              :class="{ 'selected': selectedEvent === event.id }"
              @click="selectEvent(event.id)"
            >
              <div class="event-details">
                <h3>{{ event.name }}</h3>
                <p class="event-date">
                  <i class="fas fa-calendar"></i> 
                  {{ formatDate(event.start_date) }}
                </p>
                <p class="event-location">
                  <i class="fas fa-map-marker-alt"></i> 
                  {{ event.location }}
                </p>
              </div>
              <div class="event-select">
                <div class="radio-circle"></div>
              </div>
            </div>
            
            <div v-if="!events.length" class="no-events">
              <p>No hay eventos disponibles actualmente.</p>
            </div>
          </div>
        </div>
        
        <div class="form-actions">
          <button class="btn-cancel" @click="goBack">Cancelar</button>
          <button class="btn-submit" @click="submitRegistration" :disabled="!isFormValid">
            <span style="position: relative; z-index: 2;">Registrarse</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex';

export default {
  name: 'RegistrationView',
  data() {
    return {
      visitor: {
        first_name: '',
        last_name: '',
        email: '',
        phone: '',
        identification: ''
      },
      selectedEvent: null,
      events: [],
      loading: false,
      error: null
    };
  },
  computed: {
    isFormValid() {
      return (
        this.visitor.first_name &&
        this.visitor.last_name &&
        this.visitor.email &&
        this.visitor.phone &&
        this.selectedEvent
      );
    },
    selectedEventName() {
      if (!this.selectedEvent) return '';
      const event = this.events.find(e => e.id === this.selectedEvent);
      return event ? event.name : '';
    }
  },
  created() {
    this.loadEvents();
    
    // Verificar si hay un eventId en la URL
    const eventId = this.$route.query.eventId;
    if (eventId) {
      this.selectedEvent = eventId;
    }
  },
  methods: {
    ...mapActions('events', ['fetchEvents']),
    ...mapActions('visitors', ['registerVisitorForEvent']),
    
    async loadEvents() {
      this.loading = true;
      try {
        const response = await this.fetchEvents();
        this.events = response.filter(event => event.is_active);
      } catch (error) {
        console.error('Error al cargar eventos:', error);
        this.error = 'No se pudieron cargar los eventos. Por favor, intente nuevamente.';
      } finally {
        this.loading = false;
      }
    },
    
    selectEvent(eventId) {
      this.selectedEvent = eventId;
    },
    
    formatDate(dateString) {
      const options = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      };
      return new Date(dateString).toLocaleDateString('es-ES', options);
    },
    
    async submitRegistration() {
      if (!this.isFormValid) return;
      
      this.loading = true;
      try {
        const visitorData = { ...this.visitor };
        const result = await this.registerVisitorForEvent({
          eventId: this.selectedEvent,
          visitorData
        });
        
        // Guardar datos para la página de confirmación
        const registrationData = {
          visitorName: `${this.visitor.first_name} ${this.visitor.last_name}`,
          eventId: this.selectedEvent,
          registrationCode: result.registration_code || result.data?.registration_code || ''
        };
        
        localStorage.setItem('lastRegistration', JSON.stringify(registrationData));
        
        // Redirigir a la página de confirmación con params y query como fallback
        this.$router.push({
          name: 'ConfirmationView',
          params: registrationData,
          query: registrationData
        });
      } catch (error) {
        console.error('Error al registrar visitante:', error);
        this.error = 'No se pudo completar el registro. Por favor, intente nuevamente.';
      } finally {
        this.loading = false;
      }
    },
    
    goBack() {
      this.$router.push('/kiosk/welcome');
    }
  }
};
</script>

<style scoped>
.registration-view {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding: 20px;
}

.registration-content {
  max-width: 900px;
  margin: 0 auto;
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.header {
  background-color: #512da8;
  color: white;
  padding: 20px;
  position: relative;
}

.back-button {
  background: none;
  border: none;
  color: white;
  font-size: 1rem;
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 4px;
  position: absolute;
  left: 20px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  gap: 5px;
}

.back-button:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.header h1 {
  margin: 0;
  text-align: center;
  font-size: 1.8rem;
}

.form-container {
  padding: 30px;
}

.form-section {
  margin-bottom: 30px;
}

.form-section h2 {
  font-size: 1.5rem;
  color: #333;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.event-title-highlight {
  background-color: rgba(81, 45, 168, 0.1);
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  text-align: center;
}

.event-title-highlight h3 {
  margin: 0;
  font-size: 1.2rem;
  color: #333;
}

.event-title-highlight span {
  color: #512da8;
  font-weight: 700;
}

.form-row {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.form-group {
  flex: 1;
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.form-group input {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.form-group input:focus {
  border-color: var(--ccb-navy);
  outline: none;
  box-shadow: 0 0 0 3px rgba(0, 45, 114, 0.1);
  background-color: rgba(0, 174, 239, 0.02);
}

.events-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 25px;
  margin-top: 25px;
}

.event-card {
  border: 2px solid #eee;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  justify-content: space-between;
  background: white;
}

.event-card:hover {
  border-color: var(--ccb-navy);
  box-shadow: 0 8px 20px rgba(0, 45, 114, 0.15);
  transform: translateY(-3px);
}

.event-card.selected {
  border-color: var(--ccb-navy);
  background: linear-gradient(135deg, rgba(0, 174, 239, 0.05) 0%, rgba(0, 45, 114, 0.05) 100%);
  box-shadow: 0 8px 20px rgba(0, 45, 114, 0.15);
}

.event-details {
  flex: 1;
}

.event-details h3 {
  margin: 0 0 15px 0;
  font-size: 1.3rem;
  color: var(--ccb-dark-gray);
  font-weight: 600;
}

.event-date,
.event-location {
  margin: 8px 0;
  font-size: 0.95rem;
  color: #666;
  display: flex;
  align-items: center;
  gap: 8px;
}

.event-date i {
  color: var(--ccb-orange);
}

.event-location i {
  color: var(--ccb-light-blue);
}

.event-select {
  display: flex;
  align-items: center;
}

.radio-circle {
  width: 24px;
  height: 24px;
  border: 3px solid #ddd;
  border-radius: 50%;
  position: relative;
  transition: all 0.3s;
}

.selected .radio-circle {
  border-color: var(--ccb-navy);
}

.selected .radio-circle:after {
  content: '';
  position: absolute;
  width: 12px;
  height: 12px;
  background: var(--ccb-navy);
  border-radius: 50%;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation: scaleIn 0.3s ease-out;
}

@keyframes scaleIn {
  from {
    transform: translate(-50%, -50%) scale(0);
  }
  to {
    transform: translate(-50%, -50%) scale(1);
  }
}

.no-events {
  grid-column: 1 / -1;
  text-align: center;
  padding: 40px;
  color: #666;
  font-size: 1.1rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 20px;
  margin-top: 40px;
  padding-top: 30px;
  border-top: 2px solid #eee;
}

.btn-cancel,
.btn-submit {
  padding: 14px 32px;
  border-radius: 10px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  text-transform: uppercase;
  letter-spacing: 0.8px;
}

.btn-cancel {
  background-color: white;
  border: 2px solid var(--ccb-orange);
  color: var(--ccb-orange);
}

.btn-cancel:hover {
  background-color: var(--ccb-orange);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(255, 107, 0, 0.3);
}

.btn-submit {
  background-color: #512da8;
  border: none;
  color: white;
  font-weight: bold;
  transition: all 0.3s ease;
}

.btn-submit:hover:not(:disabled) {
  background-color: #673ab7;
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 45, 114, 0.4);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background: #b0b0b0;
}

/* Add loading state animation */
.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid var(--ccb-light-gray);
  border-top-color: var(--ccb-navy);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 768px) {
  .form-row {
    flex-direction: column;
    gap: 0;
  }
  
  .events-list {
    grid-template-columns: 1fr;
  }
  
  .form-container {
    padding: 25px;
  }
  
  .form-actions {
    flex-direction: column;
    gap: 15px;
  }
  
  .btn-cancel,
  .btn-submit {
    width: 100%;
  }
}
</style>
