<template>
  <div class="modal-overlay" v-if="show" @click.self="$emit('close')">
    <div class="modal">
      <div class="modal-header">
        <h2>Registro para {{ event.title }}</h2>
        <button class="close-btn" @click="$emit('close')">
          <i class="fas fa-times"></i>
        </button>
      </div>
      
      <div class="modal-body">
        <h3 class="form-title">Registro para el evento: {{ event.title }}</h3>
        
        <div class="event-info">
          <div class="event-header">
            <strong>{{ event.title }}</strong>
            <div>{{ formatDate(event.start_date) }} - {{ event.location }}</div>
          </div>
          <div class="event-details">
            <div class="event-date">
              <i class="fas fa-calendar"></i> {{ formatDate(event.start_date) }}
            </div>
            <div class="event-location">
              <i class="fas fa-map-marker-alt"></i> {{ event.location }}
            </div>
          </div>
        </div>
        
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
        
        <form @submit.prevent="submitRegistration">
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
          
          <div class="form-actions">
            <button type="button" class="btn-cancel" @click="$emit('close')">Cancelar</button>
            <button type="submit" class="btn-submit" :disabled="!isFormValid || loading">
              <span>{{ loading ? 'Registrando...' : 'Registrarse' }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex';

export default {
  name: 'RegistrationModal',
  props: {
    show: {
      type: Boolean,
      required: true
    },
    event: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      visitor: {
        first_name: '',
        last_name: '',
        email: '',
        phone: '',
        identification: ''
      },
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
        this.visitor.phone
      );
    }
  },
  methods: {
    ...mapActions('visitors', ['registerVisitorForEvent']),
    
    formatDate(dateString) {
      if (!dateString) return 'Fecha no disponible';
      
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
      this.error = null;
      
      try {
        const visitorData = { ...this.visitor };
        await this.registerVisitorForEvent({
          eventId: this.event.id,
          visitorData
        });
        
        // Emitir evento de éxito
        this.$emit('registered', {
          eventId: this.event.id,
          visitorName: `${this.visitor.first_name} ${this.visitor.last_name}`
        });
      } catch (error) {
        console.error('Error al registrar visitante:', error);
        this.error = 'No se pudo completar el registro. Por favor, intente nuevamente.';
        this.$emit('error', this.error);
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
/* Paleta de colores CCB/Banreservas */
:root {
  --ccb-navy: #002D72;      /* Azul Marino */
  --ccb-light-blue: #00AEEF; /* Celeste */
  --ccb-orange: #FF6B00;    /* Naranja */
  --ccb-dark-gray: #2A2A2A;
  --ccb-light-gray: #F5F5F5;
  --ccb-red: #E53E3E;
  --ccb-white: #FFFFFF;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 45, 114, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal {
  background-color: white;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  box-shadow: 0 10px 30px rgba(0, 45, 114, 0.3);
  max-height: 90vh;
  overflow-y: auto;
  border: 2px solid var(--ccb-navy);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 25px;
  background: linear-gradient(135deg, var(--ccb-navy) 0%, var(--ccb-light-blue) 100%);
  color: white;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.75rem;
  color: white;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.3rem;
  cursor: pointer;
  color: white;
  transition: transform 0.3s;
}

.close-btn:hover {
  transform: rotate(90deg);
}

.modal-body {
  padding: 25px;
}

.form-title {
  color: var(--ccb-navy);
  font-size: 1.6rem;
  font-weight: 600;
  margin: 0 0 15px 0;
  text-align: center;
}

.event-info {
  background: linear-gradient(135deg, rgba(0, 174, 239, 0.05) 0%, rgba(0, 45, 114, 0.05) 100%);
  border-radius: 12px;
  padding: 18px;
  margin-bottom: 25px;
  border: 1px solid rgba(0, 45, 114, 0.2);
}

.event-header {
  text-align: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(0, 45, 114, 0.2);
}

.event-header strong {
  display: block;
  font-size: 1.4rem;
  color: var(--ccb-navy);
  margin-bottom: 5px;
}

.event-header div {
  font-size: 1rem;
  color: var(--ccb-dark-gray);
}

.event-details {
  display: flex;
  justify-content: space-between;
}

.event-date, .event-location {
  margin: 8px 0;
  font-size: 0.9rem;
  color: var(--ccb-dark-gray);
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 500;
}

.event-date i {
  color: var(--ccb-orange);
}

.event-location i {
  color: var(--ccb-light-blue);
}

.error-message {
  background-color: rgba(229, 62, 62, 0.1);
  color: var(--ccb-red);
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 20px;
  font-size: 0.95rem;
  border: 1px solid rgba(229, 62, 62, 0.3);
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
  font-weight: 600;
  color: var(--ccb-dark-gray);
  font-size: 0.95rem;
}

.form-group input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.3s;
  background-color: white;
}

.form-group input:focus {
  border-color: var(--ccb-navy);
  outline: none;
  box-shadow: 0 0 0 3px rgba(0, 45, 114, 0.1);
  background-color: rgba(0, 174, 239, 0.02);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 30px;
}

.btn-cancel, .btn-submit {
  padding: 12px 28px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  text-transform: uppercase;
  letter-spacing: 0.5px;
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
  box-shadow: 0 4px 12px rgba(255, 107, 0, 0.3);
}

.btn-submit {
  background: linear-gradient(135deg, var(--ccb-navy) 0%, var(--ccb-light-blue) 100%);
  border: none;
  color: white;
  position: relative;
  overflow: hidden;
}

.btn-submit::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, var(--ccb-light-blue) 0%, var(--ccb-orange) 100%);
  transition: left 0.5s;
  z-index: 0;
}

.btn-submit:hover:not(:disabled)::before {
  left: 0;
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 45, 114, 0.4);
  color: white;
}

.btn-submit span {
  position: relative;
  z-index: 1;
}

.btn-submit span {
  position: relative;
  z-index: 1;
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background: #b0b0b0;
}

/* Animaciones de entrada */
.modal {
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    transform: translateY(-50px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

@media (max-width: 600px) {
  .form-row {
    flex-direction: column;
    gap: 0;
  }
  
  .modal {
    width: 95%;
  }
  
  .modal-header {
    padding: 16px 20px;
  }
  
  .modal-header h2 {
    font-size: 1.4rem;
  }
  
  .modal-body {
    padding: 20px;
  }
}
</style>
