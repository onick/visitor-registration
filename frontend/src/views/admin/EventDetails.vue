<template>
  <div class="event-details">
    <div class="page-header">
      <button class="btn-back" @click="goBack">
        <i class="fas fa-arrow-left"></i> Volver
      </button>
      <h1>Detalles del Evento</h1>
    </div>

    <!-- Debug info -->
    <div v-if="debug" class="debug-info">
      <h3>Debug Info:</h3>
      <p>Event ID: {{ eventId }}</p>
      <p>Loading: {{ loading }}</p>
      <p>Error: {{ error }}</p>
      <p>Event: {{ event ? 'Loaded' : 'Not loaded' }}</p>
      <details v-if="event">
        <summary>Event Data</summary>
        <pre>{{ JSON.stringify(event, null, 2) }}</pre>
      </details>
    </div>

    <div v-if="loading" class="loading-state">
      <i class="fas fa-circle-notch fa-spin"></i>
      <p>Cargando datos del evento...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <i class="fas fa-exclamation-triangle"></i>
      <p>{{ error }}</p>
      <button class="btn-primary" @click="loadEventData">
        Reintentar
      </button>
    </div>

    <div v-else-if="!event" class="empty-state">
      <i class="fas fa-calendar-times"></i>
      <p>Evento no encontrado</p>
      <button class="btn-primary" @click="goBack">
        Volver a la lista de eventos
      </button>
    </div>

    <div v-else class="event-container">
      <div class="event-header">
        <div class="event-info">
          <h2>{{ event.title || event.name }}</h2>
          <div class="event-badges">
            <span 
              class="event-status" 
              :class="{
                'status-active': isEventActive,
                'status-upcoming': isEventUpcoming,
                'status-past': isEventPast
              }"
            >
              <i 
                class="fas" 
                :class="{
                  'fa-calendar-check': isEventActive,
                  'fa-calendar-alt': isEventUpcoming,
                  'fa-calendar-times': isEventPast
                }"
              ></i>
              {{ eventStatusText }}
            </span>
          </div>
        </div>
        <div class="event-actions">
          <button class="btn-primary" @click="editEvent">
            <i class="fas fa-edit"></i> Editar
          </button>
        </div>
      </div>

      <div class="event-details-grid">
        <div class="event-detail-card">
          <h3>Información General</h3>
          
          <!-- Imagen del evento -->
          <div class="event-image-section">
            <ImageUploader
              :event-id="eventId"
              :current-image-url="event.image_url"
              :alt-text="event.title || event.name"
              @image-uploaded="handleImageUpload"
              @image-removed="handleImageRemoval"
            />
          </div>
          
          <div class="event-detail-item">
            <span class="detail-label">Título:</span>
            <span class="detail-value">{{ event.title || event.name }}</span>
          </div>
          <div class="event-detail-item">
            <span class="detail-label">Fecha de inicio:</span>
            <span class="detail-value">{{ formatDateTime(event.start_date || event.startDate) }}</span>
          </div>
          <div class="event-detail-item">
            <span class="detail-label">Fecha de finalización:</span>
            <span class="detail-value">{{ formatDateTime(event.end_date || event.endDate) }}</span>
          </div>
          <div class="event-detail-item">
            <span class="detail-label">Ubicación:</span>
            <span class="detail-value">{{ event.location }}</span>
          </div>
          <div class="event-detail-item">
            <span class="detail-label">Estado:</span>
            <span class="detail-value status-text" :class="statusClass">
              {{ eventStatusText }}
            </span>
          </div>
          <div class="event-detail-item description">
            <span class="detail-label">Descripción:</span>
            <p class="detail-value description-text">{{ event.description || 'Sin descripción' }}</p>
          </div>
          <div class="event-detail-item">
            <span class="detail-label">Creado:</span>
            <span class="detail-value">{{ formatDateTime(event.created_at || event.createdAt) }}</span>
          </div>
          <div class="event-detail-item">
            <span class="detail-label">Última actualización:</span>
            <span class="detail-value">{{ formatDateTime(event.updated_at || event.updatedAt) }}</span>
          </div>
        </div>

        <div class="event-detail-card">
          <h3>Estadísticas</h3>
          <div class="statistics-grid">
            <div class="statistic-card">
              <i class="fas fa-users"></i>
              <div class="statistic-info">
                <span class="statistic-value">{{ eventStats.registered || 0 }}</span>
                <span class="statistic-label">Visitantes registrados</span>
              </div>
            </div>
            <div class="statistic-card">
              <i class="fas fa-user-check"></i>
              <div class="statistic-info">
                <span class="statistic-value">{{ eventStats.checkedIn || 0 }}</span>
                <span class="statistic-label">Check-ins</span>
              </div>
            </div>
            <div class="statistic-card">
              <i class="fas fa-percentage"></i>
              <div class="statistic-info">
                <span class="statistic-value">{{ attendanceRate }}%</span>
                <span class="statistic-label">Tasa de asistencia</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="visitors-section">
        <h3>Visitantes Registrados</h3>
        <div class="visitors-actions">
          <div class="search-input">
            <i class="fas fa-search"></i>
            <input 
              type="text" 
              v-model="searchTerm" 
              placeholder="Buscar visitante..." 
            />
            <button v-if="searchTerm" class="clear-search" @click="searchTerm = ''">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <button class="btn-secondary" @click="showExportDialog = true">
            <i class="fas fa-file-export"></i> Exportar
          </button>
        </div>

        <div v-if="loadingVisitors" class="loading-state">
          <i class="fas fa-circle-notch fa-spin"></i>
          <p>Cargando visitantes...</p>
        </div>

        <div v-else-if="filteredVisitors.length === 0" class="empty-state">
          <i class="fas fa-users"></i>
          <p v-if="searchTerm">No se encontraron visitantes que coincidan con la búsqueda</p>
          <p v-else>No hay visitantes registrados para este evento</p>
        </div>
  
        <div v-else class="visitors-table">
          <table>
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Email</th>
                <th>Teléfono</th>
                <th>Fecha de registro</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="visitor in filteredVisitors" :key="visitor.id">
                <td>{{ visitor.name }}</td>
                <td>{{ visitor.email }}</td>
                <td>{{ visitor.phone || 'N/A' }}</td>
                <td>{{ formatDateTime(visitor.registered_at) }}</td>
                <td>
                  <span 
                    class="visitor-status"
                    :class="visitor.checked_in ? 'status-checked' : 'status-registered'"
                  >
                    {{ visitor.checked_in ? 'Check-in completado' : 'Registrado' }}
                  </span>
                </td>
                <td>
                  <button 
                    class="btn-icon" 
                    :disabled="visitor.checked_in"
                    @click="checkInVisitor(visitor)"
                    v-if="!visitor.checked_in"
                  >
                    <i class="fas fa-user-check"></i>
                  </button>
                  <button class="btn-icon" @click="viewVisitorDetails(visitor)">
                    <i class="fas fa-eye"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    <!-- Diálogo de exportación -->
    <teleport to="body">
      <div v-if="showExportDialog" class="modal-overlay" @click="showExportDialog = false">
        <div class="modal-content" @click.stop>
          <ExportDialog
            :event-id="eventId"
            @close="showExportDialog = false"
          />
        </div>
      </div>
    </teleport>
  </div>
</template>

<script>
import { mapActions } from 'vuex';
import ExportDialog from '@/components/ExportDialog.vue';
import ImageUploader from '@/components/ImageUploader.vue';
import NotificationService from '@/services/notificationService';

export default {
  name: 'EventDetails',
  components: {
    ExportDialog,
    ImageUploader
  },
  data() {
    return {
      eventId: null,
      event: null,
      visitors: [],
      eventStats: {
        registered: 0,
        checkedIn: 0
      },
      loading: true,
      loadingVisitors: true,
      error: null,
      searchTerm: '',
      debug: true, // Activar modo debug
      showExportDialog: false
    };
  },
  computed: {
    isEventActive() {
      if (!this.event) return false;
      const now = new Date();
      const startDate = new Date(this.event.start_date || this.event.startDate);
      const endDate = new Date(this.event.end_date || this.event.endDate);
      return startDate <= now && endDate >= now;
    },
    isEventUpcoming() {
      if (!this.event) return false;
      const now = new Date();
      const startDate = new Date(this.event.start_date || this.event.startDate);
      return startDate > now;
    },
    isEventPast() {
      if (!this.event) return false;
      const now = new Date();
      const endDate = new Date(this.event.end_date || this.event.endDate);
      return endDate < now;
    },
    eventStatusText() {
      if (this.isEventActive) return 'Evento en curso';
      if (this.isEventUpcoming) return 'Próximo evento';
      if (this.isEventPast) return 'Evento finalizado';
      return 'Estado desconocido';
    },
    statusClass() {
      if (this.isEventActive) return 'status-active';
      if (this.isEventUpcoming) return 'status-upcoming';
      if (this.isEventPast) return 'status-past';
      return '';
    },
    attendanceRate() {
      if (!this.eventStats.registered) return 0;
      const rate = (this.eventStats.checkedIn / this.eventStats.registered) * 100;
      return Math.round(rate);
    },
    filteredVisitors() {
      if (!this.searchTerm) return this.visitors;
      
      const searchLower = this.searchTerm.toLowerCase();
      return this.visitors.filter(visitor => 
        visitor.name.toLowerCase().includes(searchLower) ||
        visitor.email.toLowerCase().includes(searchLower) ||
        (visitor.phone && visitor.phone.includes(searchLower))
      );
    }
  },
  methods: {
    ...mapActions({
      fetchEventById: 'events/fetchEventById',
      fetchEventVisitors: 'events/fetchEventVisitors',
      checkInVisitorAction: 'events/checkInVisitor'
    }),
    
    async loadEventData() {
      this.loading = true;
      this.error = null;
      
      console.log('=== INICIO CARGA DE EVENTO ===');
      console.log('Event ID desde ruta:', this.eventId);
      console.log('Tipo de eventId:', typeof this.eventId);
      
      // Validar ID nuevamente por seguridad
      if (!this.eventId || isNaN(this.eventId)) {
        console.error('ID de evento inválido o no numérico:', this.eventId);
        this.error = `No se pudo cargar el evento: ID inválido (${this.eventId})`;
        this.loading = false;
        return;
      }
      
      try {
        console.log('Llamando a fetchEventById...');
        const eventData = await this.fetchEventById(this.eventId);
        console.log('Respuesta de fetchEventById:', eventData);
        
        if (!eventData) {
          throw new Error('No se recibieron datos del evento');
        }
        
        this.event = eventData;
        console.log('Evento asignado a componente:', this.event);
        
        // Actualizar estadísticas desde el evento
        if (this.event) {
          this.eventStats.registered = this.event.registeredCount || this.event.registered_count || 0;
          this.eventStats.checkedIn = this.event.checkedInCount || this.event.checked_in_count || 0;
        }
        
        await this.loadVisitors();
      } catch (error) {
        console.error('ERROR al cargar datos del evento:', error);
        console.error('Stack:', error.stack);
        
        // Mensajes de error específicos según el tipo de error
        if (error.response) {
          if (error.response.status === 404) {
            this.error = `El evento con ID ${this.eventId} no existe o fue eliminado.`;
          } else if (error.response.status === 401 || error.response.status === 403) {
            this.error = 'No tienes permisos para ver este evento. Por favor, inicia sesión nuevamente.';
          } else {
            this.error = `Error del servidor: ${error.response.status} - ${error.response.data?.message || 'Error desconocido'}`;
          }
        } else if (error.message.includes('Network Error')) {
          this.error = 'No se pudo conectar con el servidor. Por favor, verifica tu conexión a internet.';
        } else {
          this.error = 'No se pudo cargar la información del evento. Por favor, intenta nuevamente.';
        }
      } finally {
        this.loading = false;
        console.log('=== FIN CARGA DE EVENTO ===');
      }
    },
    
    async loadVisitors() {
      this.loadingVisitors = true;
      
      try {
        // Si no tenemos ID de evento, no intentamos cargar visitantes
        if (!this.eventId || isNaN(this.eventId)) {
          console.warn('No se pueden cargar visitantes sin un ID de evento válido');
          this.visitors = [];
          return;
        }
        
        console.log('Cargando visitantes para evento ID:', this.eventId);
        const visitors = await this.fetchEventVisitors(this.eventId);
        console.log('Visitantes recibidos:', visitors);
        
        if (!visitors || !Array.isArray(visitors)) {
          console.warn('Formato de respuesta inválido para visitantes:', visitors);
          this.visitors = [];
          return;
        }
        
        this.visitors = visitors;
        
        // Actualizar estadísticas
        this.eventStats.registered = this.visitors.length;
        this.eventStats.checkedIn = this.visitors.filter(v => v.checked_in).length;
        
        console.log('Estadísticas actualizadas:', this.eventStats);
      } catch (error) {
        console.error('Error al cargar visitantes:', error);
        console.error('Detalles:', error.response?.data);
        this.visitors = [];  // Inicializar como arreglo vacío para evitar errores
        
        // No mostramos un error crítico para los visitantes, pero podríamos
        // mostrar una notificación o un mensaje discreto
      } finally {
        this.loadingVisitors = false;
      }
    },
    
    goBack() {
      this.$router.push('/admin/events');
    },
    
    editEvent() {
      // Para implementación futura: abrir modal de edición o navegar a la página de edición
      alert('Esta funcionalidad estará disponible próximamente.');
    },
    
    async checkInVisitor(visitor) {
      try {
        await this.checkInVisitorAction({
          eventId: this.eventId,
          visitorId: visitor.id
        });
        
        // Actualizar visitante localmente
        const index = this.visitors.findIndex(v => v.id === visitor.id);
        if (index !== -1) {
          this.visitors[index].checked_in = true;
          this.eventStats.checkedIn++;
        }
        
        NotificationService.success('Check-in completado exitosamente');
      } catch (error) {
        console.error('Error al realizar check-in:', error);
        NotificationService.error('Error al realizar el check-in');
      }
    },
    
    viewVisitorDetails(visitor) {
      // Para implementación futura: mostrar detalles del visitante
      alert(`Detalles del visitante: ${visitor.name}`);
    },
    
    formatDateTime(dateString) {
      if (!dateString) return 'N/A';
      
      const date = new Date(dateString);
      return date.toLocaleString('es-ES', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    },
    
    handleImageUpload(imageUrl) {
      // Actualizar la imagen del evento en el estado local
      if (this.event) {
        this.event.image_url = imageUrl;
      }
      NotificationService.success('Imagen del evento actualizada');
    },
    
    handleImageRemoval() {
      // Eliminar la imagen del evento en el estado local
      if (this.event) {
        this.event.image_url = null;
      }
      NotificationService.info('Imagen del evento eliminada');
    }
  },
  mounted() {
    console.log('=== COMPONENTE MONTADO ===');
    console.log('Params de ruta:', this.$route.params);
    
    // Verificar que el ID sea un número válido
    const id = this.$route.params.id;
    
    if (!id) {
      console.error('ID de evento no proporcionado en la ruta');
      this.error = 'ID de evento no proporcionado';
      this.loading = false;
      return;
    }
    
    const parsedId = parseInt(id);
    if (isNaN(parsedId)) {
      console.error('ID de evento inválido (no es un número):', id);
      this.error = `ID de evento inválido: ${id}`;
      this.loading = false;
      return;
    }
    
    // Asignar ID validado
    this.eventId = parsedId;
    console.log('Event ID parseado:', this.eventId);
    
    // Cargar datos solo si tenemos un ID válido
    this.loadEventData();
  }
};
</script>

<style scoped>
.event-details {
  width: 100%;
}

.debug-info {
  background-color: #f0f0f0;
  border: 2px solid #666;
  border-radius: 4px;
  margin: 20px 0;
  padding: 15px;
}

.debug-info h3 {
  margin-top: 0;
}

.debug-info pre {
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow-x: auto;
  padding: 10px;
}

.page-header {
  align-items: center;
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.btn-back {
  align-items: center;
  background-color: #f5f7fa;
  border: 1px solid #ddd;
  border-radius: 4px;
  color: #333;
  cursor: pointer;
  display: flex;
  font-size: 14px;
  gap: 8px;
  padding: 8px 12px;
  transition: background-color 0.2s;
}

.btn-back:hover {
  background-color: #e9ecef;
}

.loading-state, .error-state, .empty-state {
  align-items: center;
  color: #666;
  display: flex;
  flex-direction: column;
  font-size: 16px;
  gap: 15px;
  justify-content: center;
  margin: 40px 0;
  min-height: 150px;
  text-align: center;
}

.loading-state i, .error-state i, .empty-state i {
  color: #999;
  font-size: 48px;
  opacity: 0.5;
}

.error-state {
  color: #d9534f;
}

.event-container {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.event-header {
  align-items: center;
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.event-info h2 {
  color: #333;
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 10px 0;
}

.event-badges {
  display: flex;
  gap: 10px;
}

.event-status {
  align-items: center;
  border-radius: 20px;
  display: flex;
  font-size: 14px;
  gap: 5px;
  padding: 5px 10px;
}

.status-active {
  background-color: #e3f2fd;
  color: #0d6efd;
}

.status-upcoming {
  background-color: #e9f9ee;
  color: #198754;
}

.status-past {
  background-color: #f5f5f5;
  color: #6c757d;
}

.status-text.status-active {
  color: #0d6efd;
}

.status-text.status-upcoming {
  color: #198754;
}

.status-text.status-past {
  color: #6c757d;
}

.btn-primary {
  background-color: #3a86ff;
  border: none;
  border-radius: 4px;
  color: white;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  padding: 10px 15px;
  transition: background-color 0.2s;
}

.btn-primary:hover {
  background-color: #2a76ef;
}

.btn-secondary {
  background-color: #f5f7fa;
  border: 1px solid #ddd;
  border-radius: 4px;
  color: #333;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  padding: 9px 15px;
  transition: background-color 0.2s;
}

.btn-secondary:hover {
  background-color: #e9ecef;
}

.event-details-grid {
  display: grid;
  gap: 30px;
  grid-template-columns: 3fr 2fr;
}

.event-detail-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 20px;
}

.event-detail-card h3 {
  color: #333;
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 20px 0;
}

.event-detail-item {
  display: flex;
  font-size: 14px;
  margin-bottom: 15px;
}

.detail-label {
  color: #666;
  flex: 0 0 150px;
  font-weight: 500;
}

.detail-value {
  color: #333;
  flex-grow: 1;
}

.description {
  flex-direction: column;
}

.description .detail-label {
  margin-bottom: 5px;
}

.event-image-section {
  margin-bottom: 30px;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
}

.description-text {
  background-color: #f9f9f9;
  border-radius: 4px;
  line-height: 1.5;
  margin: 0;
  padding: 10px;
  white-space: pre-line;
}

.statistics-grid {
  display: grid;
  gap: 15px;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
}

.statistic-card {
  align-items: center;
  background-color: #f9f9f9;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 15px;
  text-align: center;
}

.statistic-card i {
  color: #3a86ff;
  font-size: 24px;
}

.statistic-info {
  display: flex;
  flex-direction: column;
}

.statistic-value {
  color: #333;
  font-size: 20px;
  font-weight: 600;
}

.statistic-label {
  color: #666;
  font-size: 12px;
}

.visitors-section {
  margin-top: 20px;
}

.visitors-section h3 {
  color: #333;
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 20px 0;
}

.visitors-actions {
  align-items: center;
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.search-input {
  position: relative;
  width: 300px;
}

.search-input i {
  color: #666;
  left: 12px;
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
}

.search-input input {
  background-color: #f5f7fa;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  padding: 10px 10px 10px 35px;
  width: 100%;
}

.clear-search {
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  padding: 0;
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
}

.visitors-table {
  overflow-x: auto;
}

table {
  border-collapse: collapse;
  width: 100%;
}

th, td {
  border-bottom: 1px solid #eee;
  padding: 12px 15px;
  text-align: left;
}

th {
  background-color: #f9f9f9;
  color: #333;
  font-size: 14px;
  font-weight: 600;
}

td {
  color: #555;
  font-size: 14px;
}

.visitor-status {
  border-radius: 20px;
  display: inline-block;
  font-size: 12px;
  padding: 4px 8px;
}

.status-registered {
  background-color: #e9f9ee;
  color: #198754;
}

.status-checked {
  background-color: #e3f2fd;
  color: #0d6efd;
}

.btn-icon {
  align-items: center;
  background-color: transparent;
  border: none;
  border-radius: 4px;
  color: #666;
  cursor: pointer;
  display: inline-flex;
  height: 32px;
  justify-content: center;
  transition: all 0.2s;
  width: 32px;
}

.btn-icon:hover {
  background-color: rgba(0, 0, 0, 0.05);
  color: #333;
}

.btn-icon:disabled {
  color: #ccc;
  cursor: not-allowed;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  display: flex;
  align-items: center;
  justify-content: center;
}

@media (max-width: 992px) {
  .event-details-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .event-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .event-actions {
    width: 100%;
  }
  
  .visitors-actions {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .search-input {
    width: 100%;
  }
}
</style>
