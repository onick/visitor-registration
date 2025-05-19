<template>
  <div class="events-view">
    <h1>Gestión de Eventos</h1>
    <p>Administración de eventos del Centro Cultural Banreservas</p>
    
    <div class="actions-bar">
      <div class="search-container">
        <div class="search-input">
          <i class="fas fa-search"></i>
          <input 
            type="text" 
            v-model="searchTerm" 
            placeholder="Buscar eventos..." 
            @input="filterEvents"
          />
          <button v-if="searchTerm" class="clear-search" @click="clearSearch">
            <i class="fas fa-times"></i>
          </button>
        </div>
      </div>
      
      <div class="filter-container">
        <div class="filter-group">
          <label>Estado:</label>
          <select v-model="statusFilter" @change="filterEvents">
            <option value="all">Todos</option>
            <option value="enabled">Habilitados</option>
            <option value="disabled">Deshabilitados</option>
            <option value="ongoing">En curso</option>
            <option value="upcoming">Próximos</option>
            <option value="past">Pasados</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>Ordenar por:</label>
          <select v-model="sortBy" @change="filterEvents">
            <option value="date_asc">Fecha (ascendente)</option>
            <option value="date_desc">Fecha (descendente)</option>
            <option value="name_asc">Nombre (A-Z)</option>
            <option value="name_desc">Nombre (Z-A)</option>
            <option value="attendees_desc">Asistentes (mayor a menor)</option>
          </select>
        </div>
      </div>
      
      <button class="btn-primary" @click="openCreateEventModal">
        <i class="fas fa-plus"></i> Nuevo Evento
      </button>
    </div>
    
    <div class="events-container">
      <div v-if="isLoading" class="loading-state">
        <i class="fas fa-circle-notch fa-spin"></i>
        <p>Cargando eventos...</p>
      </div>
      
      <div v-else-if="filteredEvents.length === 0" class="empty-state">
        <i class="fas fa-calendar-times"></i>
        <p v-if="searchTerm">No se encontraron eventos que coincidan con "{{ searchTerm }}"</p>
        <p v-else>No hay eventos disponibles</p>
        <button class="btn-secondary" @click="openCreateEventModal">
          Crear Nuevo Evento
        </button>
      </div>
      
      <div v-else class="events-grid">
        <div 
          v-for="event in filteredEvents" 
          :key="event.id" 
          class="event-card"
          :class="{
            'event-active': isEventActive(event),
            'event-upcoming': isEventUpcoming(event),
            'event-past': isEventPast(event)
          }"
        >
          <div class="event-header">
            <div class="event-date">
              <span class="event-day">{{ formatDay(event.startDate || event.start_date) }}</span>
              <span class="event-month">{{ formatMonth(event.startDate || event.start_date) }}</span>
            </div>
            <div class="event-actions">
              <button class="btn-icon" @click="editEvent(event)">
                <i class="fas fa-edit"></i>
              </button>
              <button class="btn-icon" @click="confirmDeleteEvent(event)">
                <i class="fas fa-trash-alt"></i>
              </button>
            </div>
          </div>
          
          <div class="event-body">
            <h3 class="event-name">{{ event.name || event.title }}</h3>
            <p class="event-time">
              <i class="far fa-clock"></i>
              {{ formatTime(event.startDate || event.start_date) }} - {{ formatTime(event.endDate || event.end_date) }}
            </p>
            <p class="event-location">
              <i class="fas fa-map-marker-alt"></i>
              {{ event.location }}
            </p>
            <p class="event-description">{{ truncateDescription(event.description) }}</p>
          </div>
          
          <div class="event-footer">
            <div class="event-stats">
              <div class="stat">
                <i class="fas fa-user-check"></i>
                <span>{{ event.registeredCount || event.registered_count || 0 }} registrados</span>
              </div>
              <div class="stat">
                <i class="fas fa-users"></i>
                <span>{{ event.checkedInCount || event.checked_in_count || 0 }} asistentes</span>
              </div>
            </div>
            <button class="btn-text" @click="viewEventDetails(event)">
              Ver Detalles
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Modal para crear/editar evento -->
    <div v-if="showEventModal" class="modal-overlay" @click.self="closeEventModal">
      <div class="modal-container">
        <div class="modal-header">
          <h2>{{ isEditMode ? 'Editar Evento' : 'Crear Nuevo Evento' }}</h2>
          <button class="btn-close" @click="closeEventModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="saveEvent" class="event-form">
            <div class="form-group">
              <label for="eventName">Nombre del Evento *</label>
              <input 
                type="text" 
                id="eventName" 
                v-model="eventForm.name" 
                required
                placeholder="Ingrese el nombre del evento"
              />
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label for="eventStartDate">Fecha de Inicio *</label>
                <input 
                  type="datetime-local" 
                  id="eventStartDate" 
                  v-model="eventForm.startDate" 
                  required
                />
              </div>
              
              <div class="form-group">
                <label for="eventEndDate">Fecha de Finalización *</label>
                <input 
                  type="datetime-local" 
                  id="eventEndDate" 
                  v-model="eventForm.endDate" 
                  required
                />
              </div>
            </div>
            
            <div class="form-group">
              <label for="eventLocation">Ubicación *</label>
              <input 
                type="text" 
                id="eventLocation" 
                v-model="eventForm.location" 
                required
                placeholder="Ingrese la ubicación del evento"
              />
            </div>
            
            <div class="form-group">
              <label for="eventDescription">Descripción</label>
              <textarea 
                id="eventDescription" 
                v-model="eventForm.description" 
                rows="4"
                placeholder="Ingrese una descripción del evento"
              ></textarea>
            </div>
            
            <div class="form-group">
              <label for="eventCapacity">Capacidad</label>
              <input 
                type="number" 
                id="eventCapacity" 
                v-model="eventForm.capacity" 
                min="1"
                placeholder="Ingrese la capacidad máxima del evento"
              />
            </div>
            
            <div class="form-group">
              <label for="eventType">Tipo de evento</label>
              <select 
                id="eventType" 
                v-model="eventForm.type"
                required
              >
                <option value="cine">Cine</option>
                <option value="exposición">Exposición</option>
                <option value="charla">Charla</option>
                <option value="taller">Taller</option>
                <option value="concierto">Concierto</option>
                <option value="otro">Otro</option>
              </select>
            </div>
            
            <div class="form-actions">
              <button type="button" class="btn-secondary" @click="closeEventModal">
                Cancelar
              </button>
              <button type="submit" class="btn-primary">
                {{ isEditMode ? 'Guardar Cambios' : 'Crear Evento' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
    
    <!-- Modal de confirmación para eliminar evento -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="closeDeleteModal">
      <div class="modal-container delete-modal">
        <div class="modal-header">
          <h2>Confirmar Eliminación</h2>
          <button class="btn-close" @click="closeDeleteModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <p class="delete-message">
            ¿Está seguro que desea eliminar el evento <strong>{{ eventToDelete?.name || eventToDelete?.title }}</strong>?
          </p>
          <p class="delete-warning">
            <i class="fas fa-exclamation-triangle"></i>
            Esta acción no se puede deshacer y eliminará todos los registros de visitantes asociados.
          </p>
          
          <div class="form-actions">
            <button type="button" class="btn-secondary" @click="closeDeleteModal">
              Cancelar
            </button>
            <button type="button" class="btn-danger" @click="deleteEvent">
              Eliminar Evento
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex';

export default {
  name: 'EventsView',
  data() {
    return {
      searchTerm: '',
      statusFilter: 'all',
      sortBy: 'date_asc',
      filteredEvents: [],
      isLoading: false,
      showEventModal: false,
      showDeleteModal: false,
      isEditMode: false,
      eventToDelete: null,
      eventForm: {
        name: '',
        startDate: '',
        endDate: '',
        location: '',
        description: '',
        capacity: null
      }
    };
  },
  computed: {
    ...mapGetters({
      events: 'events/allEvents'
    })
  },
  methods: {
    ...mapActions('events', [
      'fetchEvents', 
      'createEvent',
      'updateEvent',
      'removeEvent'
    ]),
    
    async loadEvents() {
      this.isLoading = true;
      try {
        await this.fetchEvents();
        this.filterEvents();
      } catch (error) {
        console.error('Error al cargar eventos:', error);
      } finally {
        this.isLoading = false;
      }
    },
    
    filterEvents() {
      let filtered = [...this.events];
      
      // Filtrar por término de búsqueda
      if (this.searchTerm) {
        const searchLower = this.searchTerm.toLowerCase();
        filtered = filtered.filter(event => {
          const eventName = event.name || event.title || '';
          return eventName.toLowerCase().includes(searchLower) || 
            event.location.toLowerCase().includes(searchLower) || 
            (event.description || '').toLowerCase().includes(searchLower);
        });
      }
      
      // Filtrar por estado
      const now = new Date();
      if (this.statusFilter !== 'all') {
        filtered = filtered.filter(event => {
          const startDate = new Date(event.startDate || event.start_date);
          const endDate = new Date(event.endDate || event.end_date);
          
          switch (this.statusFilter) {
            case 'enabled':
              return event.isActive || event.is_active;
            case 'disabled':
              return !(event.isActive || event.is_active);
            case 'ongoing':
              return (event.isActive || event.is_active) && startDate <= now && endDate >= now;
            case 'upcoming':
              return (event.isActive || event.is_active) && startDate > now;
            case 'past':
              return endDate < now;
            default:
              return true;
          }
        });
      }
      
      // Ordenar eventos
      filtered.sort((a, b) => {
        switch (this.sortBy) {
          case 'date_asc':
            return new Date(a.startDate || a.start_date) - new Date(b.startDate || b.start_date);
          case 'date_desc':
            return new Date(b.startDate || b.start_date) - new Date(a.startDate || a.start_date);
          case 'name_asc':
            return (a.name || a.title || '').localeCompare(b.name || b.title || '');
          case 'name_desc':
            return (b.name || b.title || '').localeCompare(a.name || a.title || '');
          case 'attendees_desc':
            return (b.checkedInCount || b.checked_in_count || 0) - (a.checkedInCount || a.checked_in_count || 0);
          default:
            return 0;
        }
      });
      
      this.filteredEvents = filtered;
    },
    
    clearSearch() {
      this.searchTerm = '';
      this.filterEvents();
    },
    
    isEventActive(event) {
      const now = new Date();
      const startDate = new Date(event.startDate || event.start_date);
      const endDate = new Date(event.endDate || event.end_date);
      return startDate <= now && endDate >= now;
    },
    
    isEventUpcoming(event) {
      const now = new Date();
      const startDate = new Date(event.startDate || event.start_date);
      return startDate > now;
    },
    
    isEventPast(event) {
      const now = new Date();
      const endDate = new Date(event.endDate || event.end_date);
      return endDate < now;
    },
    
    formatDay(dateString) {
      const date = new Date(dateString);
      return date.getDate();
    },
    
    formatMonth(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString('es-ES', { month: 'short' });
    },
    
    formatTime(dateString) {
      const date = new Date(dateString);
      return date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
    },
    
    truncateDescription(description) {
      if (!description) return '';
      return description.length > 100 ? description.substring(0, 97) + '...' : description;
    },
    
    openCreateEventModal() {
      this.isEditMode = false;
      this.resetEventForm();
      this.showEventModal = true;
    },
    
    editEvent(event) {
      this.isEditMode = true;
      this.eventForm = {
        id: event.id,
        name: event.name || event.title,
        startDate: this.formatDateTimeForInput(event.startDate || event.start_date),
        endDate: this.formatDateTimeForInput(event.endDate || event.end_date),
        location: event.location,
        description: event.description || '',
        capacity: event.capacity || null,
        type: event.type || 'otro'
      };
      this.showEventModal = true;
    },
    
    formatDateTimeForInput(dateString) {
      const date = new Date(dateString);
      return new Date(date.getTime() - (date.getTimezoneOffset() * 60000))
        .toISOString()
        .slice(0, 16);
    },
    
    closeEventModal() {
      this.showEventModal = false;
      this.resetEventForm();
    },
    
    resetEventForm() {
      this.eventForm = {
        name: '',
        startDate: '',
        endDate: '',
        location: '',
        description: '',
        capacity: null,
        type: 'otro'  // Valor por defecto para el tipo
      };
    },
    
    async saveEvent() {
      try {
        // Validar fechas
        if (!this.eventForm.startDate || !this.eventForm.endDate) {
          alert('Las fechas de inicio y finalización son obligatorias');
          return;
        }
        
        if (new Date(this.eventForm.startDate) >= new Date(this.eventForm.endDate)) {
          alert('La fecha de inicio debe ser anterior a la fecha de finalización');
          return;
        }
        
        // Validar campos obligatorios
        if (!this.eventForm.name || !this.eventForm.location) {
          alert('El nombre y la ubicación son campos obligatorios');
          return;
        }
        
        // Mostrar indicador de carga
        this.isLoading = true;
        
        if (this.isEditMode) {
          await this.updateEvent(this.eventForm);
          this.isLoading = false;
          this.closeEventModal();
          this.filterEvents();
          alert('Evento actualizado correctamente');
        } else {
          await this.createEvent(this.eventForm);
          this.isLoading = false;
          this.closeEventModal();
          this.filterEvents();
          alert('Evento creado correctamente');
        }
      } catch (error) {
        this.isLoading = false;
        console.error('Error al guardar el evento:', error);
        
        // Mostrar mensaje de error amigable
        let errorMessage = 'Ocurrió un error al guardar el evento.';
        
        if (error.response) {
          if (error.response.data && error.response.data.error) {
            errorMessage = error.response.data.error;
          } else {
            errorMessage = `Error del servidor: ${error.response.status}`;
          }
        } else if (error.message) {
          errorMessage = error.message;
        }
        
        alert(`Error: ${errorMessage}`);
      }
    },
    
    confirmDeleteEvent(event) {
      this.eventToDelete = event;
      this.showDeleteModal = true;
    },
    
    closeDeleteModal() {
      this.showDeleteModal = false;
      this.eventToDelete = null;
    },
    
    async deleteEvent() {
      if (!this.eventToDelete) return;
      
      try {
        await this.removeEvent(this.eventToDelete.id);
        this.closeDeleteModal();
        this.filterEvents();
      } catch (error) {
        console.error('Error al eliminar el evento:', error);
      }
    },
    
    viewEventDetails(event) {
      console.log('Navegando a detalles del evento:', event.id);
      this.$router.push(`/admin/events/${event.id}`);
    }
  },
  mounted() {
    this.loadEvents();
  }
};
</script>

<style scoped>
.events-view {
  width: 100%;
}

h1 {
  color: var(--color-dark);
  margin-bottom: 10px;
}

.actions-bar {
  align-items: center;
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  justify-content: space-between;
  margin-bottom: 20px;
}

.search-container {
  flex-grow: 1;
  max-width: 400px;
}

.search-input {
  position: relative;
}

.search-input i {
  color: var(--color-dark-light);
  left: 12px;
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
}

.search-input input {
  background-color: var(--color-background-light);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  font-size: 14px;
  padding: 10px 10px 10px 35px;
  width: 100%;
}

.clear-search {
  background: none;
  border: none;
  color: var(--color-dark-lighter);
  cursor: pointer;
  padding: 0;
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
}

.filter-container {
  display: flex;
  gap: 15px;
}

.filter-group {
  align-items: center;
  display: flex;
  gap: 8px;
}

.filter-group label {
  color: var(--color-dark);
  font-size: 14px;
}

.filter-group select {
  background-color: var(--color-background-light);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  font-size: 14px;
  padding: 8px 10px;
}

.btn-primary {
  background-color: var(--color-primary);
  border: none;
  border-radius: var(--border-radius);
  color: white;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  padding: 10px 15px;
  transition: background-color 0.2s;
}

.btn-primary:hover {
  background-color: var(--color-primary-dark);
}

.btn-secondary {
  background-color: var(--color-secondary);
  border: none;
  border-radius: var(--border-radius);
  color: white;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  padding: 9px 15px;
  transition: background-color 0.2s;
}

.btn-secondary:hover {
  background-color: var(--color-secondary-dark);
}

.btn-danger {
  background-color: var(--color-danger);
  border: none;
  border-radius: var(--border-radius);
  color: white;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  padding: 10px 15px;
  transition: background-color 0.2s;
}

.btn-danger:hover {
  background-color: #d73c2c;
}

.btn-text {
  background: none;
  border: none;
  color: var(--color-secondary);
  cursor: pointer;
  font-size: 14px;
  padding: 0;
  text-decoration: underline;
}

.btn-icon {
  align-items: center;
  background-color: transparent;
  border: none;
  border-radius: var(--border-radius);
  color: var(--color-dark-light);
  cursor: pointer;
  display: flex;
  height: 32px;
  justify-content: center;
  transition: all 0.2s;
  width: 32px;
}

.btn-icon:hover {
  background-color: rgba(0, 0, 0, 0.05);
  color: var(--color-dark);
}

.loading-state, .empty-state {
  align-items: center;
  color: var(--color-dark-light);
  display: flex;
  flex-direction: column;
  font-size: 16px;
  gap: 15px;
  justify-content: center;
  min-height: 200px;
  text-align: center;
}

.loading-state i, .empty-state i {
  color: var(--color-dark-lighter);
  font-size: 48px;
  opacity: 0.5;
}

.events-grid {
  display: grid;
  gap: 20px;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
}

.event-card {
  background-color: #fff;
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: box-shadow 0.2s, transform 0.2s;
}

.event-card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}

.event-active {
  border-left: 4px solid var(--color-success);
}

.event-upcoming {
  border-left: 4px solid var(--color-secondary);
}

.event-past {
  border-left: 4px solid var(--color-dark-lighter);
}

.event-header {
  align-items: center;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  padding: 15px;
}

.event-date {
  align-items: center;
  background-color: var(--color-background-light);
  border-radius: var(--border-radius);
  display: flex;
  flex-direction: column;
  height: 60px;
  justify-content: center;
  width: 60px;
}

.event-day {
  color: var(--color-dark);
  font-size: 20px;
  font-weight: 700;
  line-height: 1;
}

.event-month {
  color: var(--color-dark-light);
  font-size: 12px;
  text-transform: uppercase;
}

.event-actions {
  display: flex;
  gap: 5px;
}

.event-body {
  flex-grow: 1;
  padding: 15px;
}

.event-name {
  color: var(--color-dark);
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 10px 0;
}

.event-time, .event-location {
  color: var(--color-dark-light);
  font-size: 14px;
  margin: 0 0 5px 0;
}

.event-time i, .event-location i {
  color: var(--color-secondary);
  margin-right: 5px;
  width: 16px;
}

.event-description {
  color: var(--color-text-light);
  font-size: 14px;
  line-height: 1.4;
  margin: 10px 0 0 0;
}

.event-footer {
  align-items: center;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  padding: 12px 15px;
}

.event-stats {
  display: flex;
  gap: 15px;
}

.stat {
  align-items: center;
  color: var(--color-dark-light);
  display: flex;
  font-size: 13px;
  gap: 5px;
}

.stat i {
  color: var(--color-primary);
}

.modal-overlay {
  align-items: center;
  background-color: rgba(71, 76, 85, 0.5);
  display: flex;
  height: 100%;
  justify-content: center;
  left: 0;
  position: fixed;
  top: 0;
  width: 100%;
  z-index: 1000;
}

.modal-container {
  background-color: #fff;
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-lg);
  max-height: 90vh;
  max-width: 600px;
  overflow-y: auto;
  width: 100%;
}

.delete-modal {
  max-width: 450px;
}

.modal-header {
  align-items: center;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  padding: 15px 20px;
}

.modal-header h2 {
  color: var(--color-dark);
  font-size: 20px;
  font-weight: 600;
  margin: 0;
}

.btn-close {
  background: none;
  border: none;
  color: var(--color-dark-lighter);
  cursor: pointer;
  font-size: 18px;
  padding: 5px;
}

.modal-body {
  padding: 20px;
}

.event-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.form-group label {
  color: var(--color-dark);
  font-size: 14px;
  font-weight: 500;
}

.form-group input, .form-group textarea, .form-group select {
  background-color: var(--color-background-light);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  font-size: 14px;
  padding: 10px;
}

.form-group textarea {
  resize: vertical;
}

.form-row {
  display: flex;
  gap: 15px;
}

.form-row .form-group {
  flex: 1;
}

.form-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 10px;
}

.delete-message {
  color: var(--color-dark);
  font-size: 16px;
  margin-bottom: 15px;
  text-align: center;
}

.delete-warning {
  align-items: center;
  background-color: #fff3cd;
  border-left: 4px solid var(--color-warning);
  color: #856404;
  display: flex;
  font-size: 14px;
  gap: 10px;
  margin-bottom: 20px;
  padding: 10px 15px;
}

@media (max-width: 768px) {
  .actions-bar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-container {
    max-width: none;
  }
  
  .filter-container {
    flex-direction: column;
    gap: 10px;
  }
  
  .form-row {
    flex-direction: column;
    gap: 15px;
  }
  
  .event-footer {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
}
</style>
