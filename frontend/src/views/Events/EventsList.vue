<template>
  <div class="events-list-view">
    <Card>
      <template #header>
        <div class="card-header-content">
          <h2 class="view-title">Eventos</h2>
          <p class="view-subtitle">Gestión de eventos y registro de visitantes</p>
        </div>
        <div class="card-header-actions">
          <Button 
            icon="fas fa-plus" 
            @click="onCreateEvent"
          >
            Nuevo Evento
          </Button>
        </div>
      </template>
      
      <AlertMessage 
        v-if="error" 
        type="danger" 
        dismissible
        :message="error"
        @dismiss="error = ''"
      />
      
      <DataTable
        :columns="columns"
        :items="events"
        :loading="loading"
        :initial-sort="{ field: 'start_date', direction: 'desc' }"
        search-placeholder="Buscar eventos..."
      >
        <template #actions>
          <Button 
            variant="light" 
            size="small" 
            icon="fas fa-filter"
            @click="showFilters = !showFilters"
          >
            Filtros
          </Button>
          
          <Button 
            variant="light" 
            size="small" 
            icon="fas fa-sync"
            :loading="loading" 
            @click="loadActiveEvents"
          >
            Actualizar
          </Button>
        </template>
        
        <template #column-name="{ value }">
          <div class="event-name">{{ value }}</div>
        </template>
        
        <template #column-status="{ item }">
          <span 
            class="status-badge" 
            :class="item.isActive || item.is_active ? 'status-active' : 'status-inactive'"
          >
            {{ (item.isActive || item.is_active) ? 'Activo' : 'Inactivo' }}
          </span>
        </template>
        
        <template #column-visitor_count="{ value }">
          <div class="visitor-count">
            <i class="fas fa-user-check"></i> {{ value || 0 }}
          </div>
        </template>
        
        <template #row-actions="{ item }">
          <Button 
            variant="light" 
            size="small" 
            icon="fas fa-eye" 
            @click="viewEvent(item)"
            title="Ver detalles"
          />
          
          <Button 
            variant="light" 
            size="small" 
            icon="fas fa-edit" 
            @click="editEvent(item)"
            title="Editar evento"
          />
          
          <Button 
            variant="light" 
            size="small" 
            icon="fas fa-qrcode" 
            @click="showQR(item)"
            title="Mostrar QR"
          />
          
          <Button 
            variant="light" 
            size="small" 
            icon="fas fa-trash" 
            @click="confirmDelete(item)"
            title="Eliminar evento"
          />
        </template>
        
        <template #empty>
          <div class="empty-state">
            <i class="fas fa-calendar-alt"></i>
            <p>No se encontraron eventos</p>
            <Button 
              variant="primary" 
              @click="onCreateEvent"
            >
              Crear Primer Evento
            </Button>
          </div>
        </template>
      </DataTable>
    </Card>
    
    <!-- Modal de filtros -->
    <Modal 
      v-model="showFilters" 
      title="Filtrar Eventos"
      size="small"
    >
      <div class="filters-form">
        <FormField
          id="date-range"
          label="Rango de Fechas"
          type="select"
          v-model="filters.dateRange"
          :options="dateRangeOptions"
        />
        
        <FormField
          id="status-filter"
          label="Estado"
          type="select"
          v-model="filters.status"
          :options="statusOptions"
        />
        
        <FormField
          id="location-filter"
          label="Ubicación"
          type="select"
          v-model="filters.location"
          :options="locationOptions"
        />
      </div>
      
      <template #footer>
        <Button 
          variant="light" 
          @click="resetFilters"
        >
          Reiniciar
        </Button>
        
        <Button 
          variant="primary" 
          @click="applyFilters"
        >
          Aplicar Filtros
        </Button>
      </template>
    </Modal>
    
    <!-- Modal de confirmación de eliminación -->
    <Modal 
      v-model="showDeleteConfirm" 
      title="Confirmar Eliminación"
      size="small"
    >
      <p>¿Está seguro que desea eliminar el evento <strong>{{ eventToDelete?.name }}</strong>?</p>
      <p class="text-danger"><small>Esta acción no puede ser revertida.</small></p>
      
      <template #footer>
        <Button 
          variant="light" 
          @click="showDeleteConfirm = false"
        >
          Cancelar
        </Button>
        
        <Button 
          variant="danger" 
          :loading="deleteLoading" 
          @click="deleteEvent"
        >
          Eliminar
        </Button>
      </template>
    </Modal>
    
    <!-- Modal para mostrar el QR -->
    <Modal 
      v-model="showQRModal" 
      title="Código QR del Evento"
      size="small"
    >
      <div class="qr-container">
        <div class="qr-code" ref="qrContainer"></div>
        <p class="qr-event-name">{{ selectedEvent?.name }}</p>
      </div>
      
      <template #footer>
        <Button 
          variant="light" 
          @click="showQRModal = false"
        >
          Cerrar
        </Button>
        
        <Button 
          variant="primary" 
          @click="downloadQR"
        >
          Descargar QR
        </Button>
      </template>
    </Modal>
  </div>
</template>

<script>
import { mapActions } from 'vuex';
import QRCode from 'qrcode';
import Button from '@/components/common/Button.vue';
import Card from '@/components/common/Card.vue';
import Modal from '@/components/common/Modal.vue';
import AlertMessage from '@/components/common/AlertMessage.vue';
import FormField from '@/components/common/FormField.vue';
import DataTable from '@/components/common/DataTable.vue';

export default {
  name: 'EventsList',
  components: {
    Button,
    Card,
    Modal,
    AlertMessage,
    FormField,
    DataTable
  },
  data() {
    return {
      events: [],
      loading: false,
      error: '',
      deleteLoading: false,
      columns: [
        { field: 'name', label: 'Nombre del Evento', sortable: true },
        { field: 'start_date', label: 'Fecha de Inicio', sortable: true, format: 'datetime' },
        { field: 'end_date', label: 'Fecha de Fin', sortable: true, format: 'datetime' },
        { field: 'location', label: 'Ubicación', sortable: true },
        { field: 'status', label: 'Estado', sortable: true, custom: true },
        { field: 'visitor_count', label: 'Visitantes', sortable: true }
      ],
      showFilters: false,
      filters: {
        dateRange: 'all',
        status: 'all',
        location: 'all'
      },
      dateRangeOptions: [
        { value: 'all', label: 'Todos' },
        { value: 'upcoming', label: 'Próximos' },
        { value: 'past', label: 'Pasados' },
        { value: 'today', label: 'Hoy' },
        { value: 'week', label: 'Esta semana' },
        { value: 'month', label: 'Este mes' }
      ],
      statusOptions: [
        { value: 'all', label: 'Todos' },
        { value: 'ACTIVE', label: 'Activo' },
        { value: 'DRAFT', label: 'Borrador' },
        { value: 'COMPLETED', label: 'Completado' },
        { value: 'CANCELLED', label: 'Cancelado' }
      ],
      locationOptions: [
        { value: 'all', label: 'Todas' }
      ],
      showDeleteConfirm: false,
      eventToDelete: null,
      showQRModal: false,
      selectedEvent: null
    };
  },
  computed: {
    uniqueLocations() {
      if (!this.events || !this.events.length) return [];
      
      // Extraer ubicaciones únicas de los eventos
      const locations = [...new Set(this.events.map(event => event.location))];
      return locations.filter(location => !!location);
    }
  },
  created() {
    this.loadActiveEvents();
  },
  watch: {
    uniqueLocations(locations) {
      // Actualizar las opciones de ubicación cuando cambian los eventos
      this.locationOptions = [
        { value: 'all', label: 'Todas' },
        ...locations.map(location => ({ value: location, label: location }))
      ];
    }
  },
  methods: {
    ...mapActions('events', ['fetchEvents', 'removeEvent']),
    
    async loadEvents(activeOnly = true) {
      this.loading = true;
      this.error = '';
      
      try {
        // Cargar eventos desde Vuex
        const events = await this.fetchEvents();
        if (activeOnly) {
          // Filtrar solo eventos activos
          this.events = events ? events.filter(event => event.isActive || event.is_active) : [];
        } else {
          this.events = events || [];
        }
      } catch (err) {
        console.error('Error al cargar eventos:', err);
        this.error = 'Error al cargar los eventos. Por favor, intente nuevamente.';
      } finally {
        this.loading = false;
      }
    },
    
    async loadActiveEvents() {
      return this.loadEvents(true);
    },
    
    formatStatus(status) {
      const statusMap = {
        'ACTIVE': 'Activo',
        'DRAFT': 'Borrador',
        'COMPLETED': 'Completado',
        'CANCELLED': 'Cancelado'
      };
      
      return statusMap[status] || status;
    },
    
    onCreateEvent() {
      this.$router.push({ name: 'EventsList' });
    },
    
    viewEvent(event) {
      this.$router.push({ 
        name: 'event-detail', 
        params: { id: event.id }
      });
    },
    
    editEvent(event) {
      this.$router.push({ 
        name: 'event-edit', 
        params: { id: event.id }
      });
    },
    
    confirmDelete(event) {
      this.eventToDelete = event;
      this.showDeleteConfirm = true;
    },
    
    async deleteEvent() {
      if (!this.eventToDelete) return;
      
      this.deleteLoading = true;
      try {
        await this.removeEvent(this.eventToDelete.id);
        
        // Eliminar el evento de la lista local
        this.events = this.events.filter(e => e.id !== this.eventToDelete.id);
        
        this.$toasted.success('Evento eliminado correctamente');
        this.showDeleteConfirm = false;
      } catch (err) {
        console.error('Error al eliminar evento:', err);
        this.error = 'Error al eliminar el evento. Por favor, intente nuevamente.';
      } finally {
        this.deleteLoading = false;
      }
    },
    
    resetFilters() {
      this.filters = {
        dateRange: 'all',
        status: 'all',
        location: 'all'
      };
    },
    
    applyFilters() {
      // Implementar lógica de filtrado aquí
      this.loadActiveEvents();
      this.showFilters = false;
    },
    
    showQR(event) {
      this.selectedEvent = event;
      this.showQRModal = true;
      
      // Generar QR en el próximo ciclo para asegurar que el contenedor esté disponible
      this.$nextTick(() => {
        // Verificar explícitamente si el contenedor existe
        if (!this.$refs.qrContainer) {
          console.warn('Contenedor QR no encontrado');
          this.error = 'Error al preparar el código QR.';
          return;
        }
        
        try {
          const qrData = JSON.stringify({
            event_id: event.id,
            event_name: event.name,
            url: `${window.location.origin}/events/${event.id}/register`
          });
          
          QRCode.toCanvas(this.$refs.qrContainer, qrData, {
            width: 250,
            margin: 2,
            color: {
              dark: '#512da8',
              light: '#ffffff'
            }
          }).catch(err => {
            console.error('Error al generar QR:', err);
            this.error = 'Error al generar el código QR.';
          });
        } catch (err) {
          console.error('Error al intentar generar QR:', err);
          this.error = 'Error al intentar generar el código QR.';
        }
      });
    },
    
    downloadQR() {
      try {
        // Verificaciones más estrictas para evitar errores
        if (!this.$refs.qrContainer) {
          console.warn('Contenedor QR no encontrado para descargar');
          this.error = 'Error al preparar la descarga del código QR.';
          return;
        }
        
        if (!this.$refs.qrContainer.toDataURL) {
          console.warn('El contenedor QR no es un canvas válido');
          this.error = 'Error al intentar descargar el código QR.';
          return;
        }
        
        const canvas = this.$refs.qrContainer;
        const dataUrl = canvas.toDataURL('image/png');
        
        const link = document.createElement('a');
        link.download = `qr-evento-${this.selectedEvent?.id || 'desconocido'}.png`;
        link.href = dataUrl;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } catch (err) {
        console.error('Error al descargar QR:', err);
        this.error = 'Error al descargar el código QR.';
      }
    }
  }
};
</script>

<style scoped>
.events-list-view {
  width: 100%;
}

.view-title {
  font-size: 22px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.view-subtitle {
  font-size: 14px;
  color: #666;
  margin: 5px 0 0 0;
}

.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-active {
  background-color: #e6f4e8;
  color: #43a047;
}

.status-inactive {
  background-color: #ffebee;
  color: #e53935;
}

.status-draft {
  background-color: #e3f2fd;
  color: #039be5;
}

.status-completed {
  background-color: #eee;
  color: #757575;
}

.status-cancelled {
  background-color: #ffebee;
  color: #e53935;
}

.event-name {
  font-weight: 500;
  color: #512da8;
}

.visitor-count {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
}

.visitor-count i {
  color: #512da8;
}

.empty-state {
  padding: 40px 20px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.empty-state i {
  font-size: 48px;
  color: #ddd;
}

.empty-state p {
  font-size: 16px;
  color: #666;
  margin: 0;
}

.filters-form {
  display: grid;
  grid-gap: 15px;
}

.qr-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px;
}

.qr-code {
  margin-bottom: 15px;
}

.qr-event-name {
  font-weight: 500;
  color: #512da8;
  text-align: center;
}

.text-danger {
  color: #e53935;
}
</style> 