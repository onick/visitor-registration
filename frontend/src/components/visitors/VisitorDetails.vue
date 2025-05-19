<template>
  <div class="visitor-details">
    <div class="details-header">
      <h3>Detalles del Visitante</h3>
      <button class="btn-close" @click="close">
        <i class="fas fa-times"></i>
      </button>
    </div>
    
    <div v-if="loading" class="loading-state">
      <i class="fas fa-circle-notch fa-spin"></i>
      <p>Cargando información del visitante...</p>
    </div>
    
    <div v-else-if="error" class="error-state">
      <i class="fas fa-exclamation-triangle"></i>
      <p>{{ error }}</p>
      <button class="btn-retry" @click="loadVisitorData">
        Reintentar
      </button>
    </div>
    
    <div v-else-if="visitor" class="details-content">
      <div class="visitor-profile">
        <div class="visitor-avatar">
          {{ getInitials(visitor.first_name, visitor.last_name) }}
        </div>
        <div class="visitor-name">
          <h4>{{ visitor.first_name }} {{ visitor.last_name }}</h4>
          <span 
            class="visitor-status"
            :class="visitor.checked_in ? 'status-checked' : 'status-pending'"
          >
            {{ visitor.checked_in ? 'Check-in completado' : 'Pendiente de check-in' }}
          </span>
        </div>
      </div>
      
      <div class="details-section">
        <h5>Información de Contacto</h5>
        <div class="details-grid">
          <div class="detail-item">
            <span class="detail-label">Email:</span>
            <span class="detail-value">{{ visitor.email || 'No disponible' }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Teléfono:</span>
            <span class="detail-value">{{ visitor.phone || 'No disponible' }}</span>
          </div>
          <div class="detail-item" v-if="visitor.identification">
            <span class="detail-label">Identificación:</span>
            <span class="detail-value">{{ visitor.identification }}</span>
          </div>
        </div>
      </div>
      
      <div class="details-section">
        <h5>Información de Registro</h5>
        <div class="details-grid">
          <div class="detail-item">
            <span class="detail-label">Evento:</span>
            <span class="detail-value">{{ eventName }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Fecha de Registro:</span>
            <span class="detail-value">{{ formatDateTime(visitor.created_at || visitor.registered_at) }}</span>
          </div>
          <div class="detail-item" v-if="visitor.checked_in">
            <span class="detail-label">Fecha de Check-in:</span>
            <span class="detail-value">{{ formatDateTime(visitor.checked_in_at) }}</span>
          </div>
        </div>
      </div>
      
      <div class="details-actions">
        <button 
          class="btn-primary" 
          v-if="!visitor.checked_in"
          @click="checkInVisitor"
          :disabled="checkingIn"
        >
          <i class="fas fa-user-check"></i>
          <span v-if="!checkingIn">Realizar Check-in</span>
          <span v-else>Procesando...</span>
        </button>
        <button class="btn-secondary" @click="editVisitor">
          <i class="fas fa-edit"></i> Editar
        </button>
      </div>
    </div>
    
    <div v-else class="empty-state">
      <i class="fas fa-user-slash"></i>
      <p>No se encontró información del visitante</p>
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex';

export default {
  name: 'VisitorDetails',
  props: {
    visitorId: {
      type: [Number, String],
      required: true
    },
    eventId: {
      type: [Number, String],
      default: null
    }
  },
  data() {
    return {
      visitor: null,
      event: null,
      loading: true,
      error: null,
      checkingIn: false
    };
  },
  computed: {
    eventName() {
      if (this.event) {
        return this.event.name || this.event.title;
      }
      return this.visitor && this.visitor.event_name ? this.visitor.event_name : 'No disponible';
    }
  },
  created() {
    this.loadVisitorData();
  },
  methods: {
    ...mapActions({
      fetchVisitorById: 'visitors/fetchVisitorById',
      fetchEventById: 'events/fetchEventById',
      checkInVisitorAction: 'events/checkInVisitor',
      updateVisitor: 'visitors/updateVisitor'
    }),
    
    async loadVisitorData() {
      this.loading = true;
      this.error = null;
      
      try {
        // Cargar datos del visitante
        this.visitor = await this.fetchVisitorById(this.visitorId);
        
        // Si tenemos un eventId, cargar datos del evento
        if (this.eventId || (this.visitor && this.visitor.event_id)) {
          const eventToFetch = this.eventId || this.visitor.event_id;
          this.event = await this.fetchEventById(eventToFetch);
        }
      } catch (error) {
        console.error('Error al cargar datos del visitante:', error);
        this.error = 'No se pudo cargar la información del visitante';
      } finally {
        this.loading = false;
      }
    },
    
    getInitials(firstName, lastName) {
      if (!firstName && !lastName) return 'VT';
      
      const firstInitial = firstName ? firstName.charAt(0).toUpperCase() : '';
      const lastInitial = lastName ? lastName.charAt(0).toUpperCase() : '';
      
      return firstInitial + lastInitial;
    },
    
    formatDateTime(dateString) {
      if (!dateString) return 'No disponible';
      
      const options = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      };
      
      return new Date(dateString).toLocaleDateString('es-ES', options);
    },
    
    async checkInVisitor() {
      if (!this.visitor || this.visitor.checked_in) return;
      
      this.checkingIn = true;
      try {
        await this.checkInVisitorAction({
          eventId: this.eventId || this.visitor.event_id,
          visitorId: this.visitor.id
        });
        
        // Actualizar estado local
        this.visitor.checked_in = true;
        this.visitor.checked_in_at = new Date().toISOString();
        
        // Notificar éxito
        this.$store.dispatch('showNotification', {
          message: `Check-in completado para ${this.visitor.first_name} ${this.visitor.last_name}`,
          type: 'success'
        });
      } catch (error) {
        console.error('Error al realizar check-in:', error);
        this.$store.dispatch('showNotification', {
          message: 'Error al realizar el check-in',
          type: 'error'
        });
      } finally {
        this.checkingIn = false;
      }
    },
    
    editVisitor() {
      this.$emit('edit', this.visitor);
    },
    
    close() {
      this.$emit('close');
    }
  }
};
</script>

<style scoped>
.visitor-details {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  width: 100%;
  max-width: 600px;
}

.details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
}

.details-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.btn-close {
  background: none;
  border: none;
  color: #777;
  font-size: 16px;
  cursor: pointer;
}

.loading-state,
.error-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
}

.loading-state i,
.error-state i,
.empty-state i {
  font-size: 36px;
  margin-bottom: 16px;
  color: #aaa;
}

.error-state i {
  color: #dc3545;
}

.btn-retry {
  margin-top: 16px;
  padding: 8px 16px;
  background-color: #f8f9fa;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

.details-content {
  padding: 20px;
}

.visitor-profile {
  display: flex;
  align-items: center;
  margin-bottom: 24px;
}

.visitor-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: #3a86ff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 500;
  margin-right: 16px;
}

.visitor-name h4 {
  margin: 0 0 8px 0;
  font-size: 20px;
  color: #333;
}

.visitor-status {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-checked {
  background-color: #d4edda;
  color: #155724;
}

.status-pending {
  background-color: #fff3cd;
  color: #856404;
}

.details-section {
  margin-bottom: 24px;
}

.details-section h5 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #555;
  border-bottom: 1px solid #eee;
  padding-bottom: 8px;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 16px;
}

.detail-item {
  display: flex;
  flex-direction: column;
}

.detail-label {
  font-size: 12px;
  color: #777;
  margin-bottom: 4px;
}

.detail-value {
  font-size: 14px;
  color: #333;
}

.details-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.btn-primary,
.btn-secondary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
}

.btn-primary {
  background-color: #3a86ff;
  color: white;
}

.btn-primary:disabled {
  background-color: #a0c4ff;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #f8f9fa;
  border: 1px solid #ddd;
  color: #333;
}

@media (max-width: 768px) {
  .details-grid {
    grid-template-columns: 1fr;
  }
}
</style>