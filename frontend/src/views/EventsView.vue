<template>
  <div class="events-view">
    <kiosk-header title="Eventos" :showBackButton="true" @back="goBack" />
    
    <div class="events-container">
      <div v-if="loading" class="loading-indicator">
        <div class="spinner"></div>
        <p>Cargando eventos...</p>
      </div>
      
      <div v-else-if="error" class="error-message">
        <div class="error-icon">
          <i class="fas fa-exclamation-circle"></i>
        </div>
        <p>{{ error }}</p>
        <button class="btn btn-primary" @click="loadEvents">
          Intentar nuevamente
        </button>
      </div>
      
      <div v-else-if="events.length === 0" class="no-events">
        <div class="info-icon">
          <i class="fas fa-info-circle"></i>
        </div>
        <p>No hay eventos disponibles en este momento.</p>
        <button class="btn btn-primary" @click="goBack">
          Volver al inicio
        </button>
      </div>
      
      <template v-else>
        <div class="events-filter">
          <button 
            class="filter-btn" 
            :class="{ active: activeFilter === 'all' }" 
            @click="setFilter('all')"
          >
            Todos
          </button>
          <button 
            class="filter-btn" 
            :class="{ active: activeFilter === 'upcoming' }" 
            @click="setFilter('upcoming')"
          >
            Próximos
          </button>
          <button 
            class="filter-btn" 
            :class="{ active: activeFilter === 'ongoing' }" 
            @click="setFilter('ongoing')"
          >
            En curso
          </button>
        </div>
        
        <div class="events-list">
          <event-card 
            v-for="event in filteredEvents" 
            :key="event.id" 
            :event="event"
            @select="openRegistrationModal(event)"
          />
        </div>
      </template>
    </div>
    
    <!-- Modal de registro rápido -->
    <registration-modal
      v-if="showRegistrationModal"
      :show="showRegistrationModal"
      :event="selectedEvent"
      @close="closeRegistrationModal"
      @registered="onRegistrationSuccess"
      @error="onRegistrationError"
    />
  </div>
</template>

<script>
import KioskHeader from '@/components/kiosk/KioskHeader.vue';
import EventCard from '@/components/kiosk/EventCard.vue';
import RegistrationModal from '@/components/kiosk/RegistrationModal.vue';
import { mapGetters, mapActions } from 'vuex';
import { checkEvents } from '@/components/EventsDebug.js';

export default {
  name: 'EventsView',
  components: {
    KioskHeader,
    EventCard,
    RegistrationModal
  },
  data() {
    return {
      activeFilter: 'all', // 'all', 'upcoming', 'ongoing'
      inactivityTimer: null,
      showRegistrationModal: false,
      selectedEvent: null,
      registrationError: null
    };
  },
  computed: {
    ...mapGetters({
      events: 'events/allEvents',
      upcomingEvents: 'events/upcomingEvents',
      ongoingEvents: 'events/ongoingEvents',
      loading: 'events/isLoading',
      error: 'events/error'
    }),
    filteredEvents() {
      switch (this.activeFilter) {
        case 'upcoming':
          return this.upcomingEvents;
        case 'ongoing':
          return this.ongoingEvents;
        case 'all':
        default:
          return this.events;
      }
    }
  },
  mounted() {
    this.loadEvents();
    this.startInactivityTimer();
  },
  updated() {
    // Verificar eventos cuando el componente se actualiza
    if (this.events.length > 0) {
      const diagnosis = checkEvents(this.$store.state.events.events, this.upcomingEvents, this.ongoingEvents);
      console.log('Diagnóstico de eventos:', diagnosis);
    }
  },
  beforeUnmount() {
    if (this.inactivityTimer) {
      clearTimeout(this.inactivityTimer);
    }
  },
  methods: {
    ...mapActions('events', ['fetchEvents']),
    
    async loadEvents() {
      try {
        console.log('Iniciando carga de eventos...');
        await this.fetchEvents();
        console.log(`Se han cargado ${this.events.length} eventos en total`);
        console.log(`Próximos eventos: ${this.upcomingEvents.length}`);
        console.log(`Eventos en curso: ${this.ongoingEvents.length}`);
        console.log('Eventos cargados correctamente');
      } catch (error) {
        console.error('Error al cargar eventos:', error);
      }
    },
    
    setFilter(filter) {
      this.activeFilter = filter;
      this.resetInactivityTimer();
    },
    
    openRegistrationModal(event) {
      this.selectedEvent = event;
      this.showRegistrationModal = true;
      this.resetInactivityTimer();
    },
    
    closeRegistrationModal() {
      this.showRegistrationModal = false;
      this.selectedEvent = null;
      this.resetInactivityTimer();
    },
    
    onRegistrationSuccess(data) {
      // Cerrar el modal
      this.showRegistrationModal = false;
      
      // Guardar datos para la página de confirmación
      const registrationData = {
        visitorName: data.visitorName,
        eventId: data.eventId
      };
      
      localStorage.setItem('lastRegistration', JSON.stringify(registrationData));
      
      // Redirigir a la pantalla de confirmación con params y query como fallback
      this.$router.push({
        name: 'ConfirmationView',
        params: registrationData,
        query: registrationData
      });
    },
    
    onRegistrationError(error) {
      this.registrationError = error;
      // Mantener el modal abierto para que el usuario pueda intentar de nuevo
      this.resetInactivityTimer();
    },
    
    startInactivityTimer() {
      clearTimeout(this.inactivityTimer);
      this.inactivityTimer = setTimeout(() => {
        this.goBack();
      }, 120000); // 2 minutos de inactividad
    },
    
    resetInactivityTimer() {
      this.startInactivityTimer();
    },
    
    goBack() {
      this.$router.push('/kiosk/welcome');
    }
  }
};
</script>

<style scoped>
.events-view {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f8f9fa;
}

.events-container {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
}

.loading-indicator, .error-message, .no-events {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid rgba(0, 123, 255, 0.2);
  border-top-color: #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-icon, .info-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.error-icon {
  color: #dc3545;
}

.info-icon {
  color: #17a2b8;
}

.events-filter {
  display: flex;
  justify-content: center;
  margin-bottom: 2rem;
  gap: 0.5rem;
}

.filter-btn {
  padding: 0.5rem 1rem;
  background-color: #fff;
  border: 1px solid #ced4da;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-btn.active {
  background-color: #007bff;
  color: white;
  border-color: #007bff;
}

.events-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: all 0.2s;
  margin-top: 1rem;
}

.btn-primary {
  background-color: #007bff;
  color: white;
  border: none;
}

.btn-primary:hover {
  background-color: #0069d9;
}

/* Estilos responsivos */
@media (max-width: 768px) {
  .events-container {
    padding: 1rem;
  }
  
  .events-list {
    grid-template-columns: 1fr;
  }
}
</style> 