<template>
  <div class="visitors-view">
    <h1>Gestión de Visitantes</h1>
    <p>Administración de visitantes registrados en eventos</p>
    
    <div v-if="loading" class="loading-overlay">
      <div class="spinner"></div>
      <p>Cargando visitantes...</p>
    </div>
    
    <div v-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="clearError" class="btn-retry">Reintentar</button>
    </div>
    
    <!-- Filtros avanzados -->
    <visitor-filter 
      :events="events" 
      @filter-change="handleFilterChange"
    />
    
    <div class="actions-bar">
      <div class="admin-actions">
        <button @click="exportVisitors" class="btn btn-secondary">
          <i class="fas fa-file-export"></i> Exportar visitantes
        </button>
        <button @click="createTestVisitor" class="btn btn-primary" :disabled="loading">
          <i class="fas fa-user-plus"></i> Crear visitante de prueba
        </button>
      </div>
    </div>
    
    <div class="debug-info">
      <div v-if="serverStatus" class="server-status">
        <strong>Estado del servidor:</strong> {{ serverStatus }}
      </div>
      <div class="api-status">
        <strong>Filtros activos:</strong> {{ JSON.stringify(activeFilters) }}
      </div>
      <div class="api-status">
        <strong>Total de visitantes cargados:</strong> {{ visitors.length }}
      </div>
      <div v-if="apiResponse" class="api-response">
        <strong>Última respuesta:</strong> 
        <pre>{{ typeof apiResponse === 'object' ? JSON.stringify(apiResponse, null, 2) : apiResponse }}</pre>
      </div>
    </div>
    
    <div v-if="!loading && !error" class="table-container">
      <div v-if="filteredVisitors.length === 0" class="empty-state">
        <i class="fas fa-users"></i>
        <p>No hay visitantes que coincidan con los filtros aplicados</p>
        <button class="btn-primary" @click="handleFilterChange({searchTerm: '', eventId: '', status: '', dateFrom: '', dateTo: ''})">
          Limpiar filtros
        </button>
      </div>
      
      <table v-else class="visitors-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Nombre</th>
            <th>Email</th>
            <th>Teléfono</th>
            <th>Evento</th>
            <th>Fecha de Registro</th>
            <th>Estado</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="visitor in filteredVisitors" :key="visitor.id">
            <td>{{ visitor.id }}</td>
            <td>{{ visitor.name || (visitor.first_name + ' ' + visitor.last_name) }}</td>
            <td>{{ visitor.email }}</td>
            <td>{{ visitor.phone || 'N/A' }}</td>
            <td>{{ visitor.event_title || visitor.event?.title || getEventName(visitor.event_id) }}</td>
            <td>{{ formatDate(visitor.check_in_time || visitor.created_at || visitor.registrationDate) }}</td>
            <td>
              <span class="status-badge" :class="getStatusClass(visitor)">
                {{ getStatusText(visitor) }}
              </span>
            </td>
            <td class="actions-cell">
              <button class="btn-icon" title="Ver detalles" @click="viewVisitorDetails(visitor)">
                <i class="fas fa-eye"></i>
              </button>
              <button class="btn-icon" title="Editar" @click="editVisitor(visitor)">
                <i class="fas fa-edit"></i>
              </button>
              <button class="btn-icon delete" title="Eliminar" @click="deleteVisitor(visitor.id)">
                <i class="fas fa-trash"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- Modal de detalles del visitante -->
    <div v-if="showVisitorDetails" class="modal-overlay" @click.self="closeVisitorDetails">
      <div class="modal-container">
        <visitor-details 
          :visitor-id="selectedVisitor.id" 
          @close="closeVisitorDetails"
          @edit="editVisitor"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapGetters, mapActions } from 'vuex';
import axios from 'axios';
import VisitorFilter from '@/components/visitors/VisitorFilter.vue';
import VisitorDetails from '@/components/visitors/VisitorDetails.vue';

export default {
  name: 'VisitorsList',
  components: {
    VisitorFilter,
    VisitorDetails
  },
  data() {
    return {
      activeFilters: {
        searchTerm: '',
        eventId: '',
        status: '',
        dateFrom: '',
        dateTo: ''
      },
      serverStatus: null,
      apiResponse: null,
      selectedVisitor: null,
      showVisitorDetails: false
    };
  },
  computed: {
    ...mapState('visitors', ['loading', 'error', 'visitors']),
    ...mapState('events', ['events']),
    
    filteredVisitors() {
      let result = this.visitors || [];
      
      // Si estamos usando búsqueda en el servidor, solo aplicamos filtros locales adicionales
      
      // Aplicar filtro de estado si está presente
      if (this.activeFilters.status) {
        switch(this.activeFilters.status) {
          case 'checked-in':
            result = result.filter(visitor => visitor.checked_in);
            break;
          case 'pending':
            result = result.filter(visitor => !visitor.checked_in);
            break;
        }
      }
      
      // Aplicar filtros de fecha, que sería mejor manejarlos en el servidor también
      if (this.activeFilters.dateFrom) {
        const fromDate = new Date(this.activeFilters.dateFrom);
        result = result.filter(visitor => {
          const createdDate = new Date(visitor.check_in_time || visitor.created_at || visitor.registrationDate);
          return createdDate >= fromDate;
        });
      }
      
      if (this.activeFilters.dateTo) {
        const toDate = new Date(this.activeFilters.dateTo);
        toDate.setHours(23, 59, 59, 999); // End of day
        result = result.filter(visitor => {
          const createdDate = new Date(visitor.check_in_time || visitor.created_at || visitor.registrationDate);
          return createdDate <= toDate;
        });
      }
      
      return result;
    }
  },
  methods: {
    ...mapActions('visitors', ['fetchVisitors', 'removeVisitor', 'clearError', 'createVisitor', 'registerVisitorForEvent']),
    ...mapActions('events', ['fetchEvents']),
    
    handleFilterChange(filters) {
      this.activeFilters = { ...filters };
      
      // Recargar visitantes con los filtros aplicados directamente al backend
      // en lugar de filtrar localmente
      const params = {};
      
      // Añadir los filtros a los parámetros de búsqueda
      if (this.activeFilters.eventId) {
        params.event_id = parseInt(this.activeFilters.eventId);
        console.log(`Filtrando por evento ID: ${params.event_id}`);
      }
      
      if (this.activeFilters.searchTerm) {
        params.search = this.activeFilters.searchTerm;
      }
      
      // Establecer límite alto para obtener todos los resultados
      params.limit = 100;
      
      // Registrar los parámetros para debug
      console.log('Enviando parámetros al servidor:', params);
      
      // Recargar visitantes con los parámetros
      this.fetchVisitors(params)
        .then(() => {
          console.log(`Visitantes cargados: ${this.visitors.length}`);
        })
        .catch(error => {
          console.error('Error al cargar visitantes con filtros:', error);
        });
    },
    
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      return date.toLocaleDateString('es-ES', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    },
    
    getEventName(eventId) {
      if (!eventId) return 'Sin evento asignado';
      const event = this.events.find(e => e.id === eventId);
      return event ? (event.name || event.title) : 'Evento desconocido';
    },
    
    getStatusClass(visitor) {
      return visitor.checked_in ? 'status-checked' : 'status-pending';
    },
    
    getStatusText(visitor) {
      return visitor.checked_in ? 'Registrado' : 'Pendiente';
    },
    
    viewVisitorDetails(visitor) {
      this.selectedVisitor = visitor;
      this.showVisitorDetails = true;
    },
    
    closeVisitorDetails() {
      this.showVisitorDetails = false;
      this.selectedVisitor = null;
    },
    
    editVisitor(visitor) {
      // Implementar edición
      this.$router.push(`/admin/visitors/${visitor.id}/edit`);
    },
    
    exportVisitors() {
      if (this.filteredVisitors.length === 0) {
        this.$store.dispatch('showNotification', {
          message: 'No hay visitantes para exportar',
          type: 'warning'
        });
        return;
      }
      
      try {
        // Crear CSV
        const headers = ['ID', 'Nombre', 'Email', 'Teléfono', 'Evento', 'Fecha de Registro', 'Estado'];
        let csvContent = headers.join(',') + '\n';
        
        this.filteredVisitors.forEach(visitor => {
          const eventName = visitor.event_title || visitor.event?.title || this.getEventName(visitor.event_id);
          const status = visitor.checked_in ? 'Registrado' : 'Pendiente';
          const row = [
            visitor.id,
            visitor.name || (visitor.first_name + ' ' + visitor.last_name) || '',
            visitor.email || '',
            visitor.phone || '',
            eventName,
            visitor.created_at ? new Date(visitor.created_at).toLocaleDateString('es-ES') : '',
            status
          ];
          
          // Escapar comas en los campos
          const formattedRow = row.map(field => {
            const stringField = String(field);
            return stringField.includes(',') ? `"${stringField}"` : stringField;
          });
          
          csvContent += formattedRow.join(',') + '\n';
        });
        
        // Crear blob y descargar
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.setAttribute('href', url);
        link.setAttribute('download', `visitantes_${new Date().toISOString().split('T')[0]}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        this.$store.dispatch('showNotification', {
          message: `${this.filteredVisitors.length} visitantes exportados correctamente`,
          type: 'success'
        });
      } catch (error) {
        console.error('Error al exportar visitantes:', error);
        this.$store.dispatch('showNotification', {
          message: 'Error al exportar visitantes',
          type: 'error'
        });
      }
    },
    
    async deleteVisitor(id) {
      if (confirm('¿Está seguro de que desea eliminar este visitante? Esta acción no se puede deshacer.')) {
        try {
          await this.removeVisitor(id);
          // Mostrar mensaje de éxito
          alert('Visitante eliminado correctamente');
        } catch (error) {
          // El error ya está en el estado
          console.error('Error al eliminar visitante:', error);
        }
      }
    },
    
    async checkServerStatus() {
      try {
        console.log('Verificando estado del servidor...');
        
        // Verificar estado del backend
        const eventsResponse = await axios.get('/events/');
        console.log('Respuesta de eventos:', eventsResponse.data);
        
        // Intentar autenticarse
        try {
          const authResponse = await axios.post('/auth/login', {
            email: 'admin@admin.com',
            password: 'Admin123!'
          });
          console.log('Respuesta de autenticación:', authResponse.data);
          localStorage.setItem('access_token', authResponse.data.access_token);
          
          // Intentar obtener visitantes con el token
          const visitorsResponse = await axios.get('/visitors/');
          console.log('Respuesta de visitantes:', visitorsResponse.data);
          this.apiResponse = visitorsResponse.data;
          
          this.serverStatus = 'El servidor está en línea y se ha obtenido acceso a los datos de visitantes';
        } catch (authError) {
          console.error('Error de autenticación:', authError);
          this.apiResponse = authError.response?.data || authError.message;
          this.serverStatus = 'El servidor está en línea pero falló la autenticación';
        }
      } catch (error) {
        console.error('Error al verificar estado del servidor:', error);
        this.apiResponse = error.response?.data || error.message;
        this.serverStatus = 'Error al contactar con el servidor: ' + error.message;
      }
    },
    
    async createTestVisitor() {
      try {
        if (!this.events || this.events.length === 0) {
          alert('No hay eventos disponibles para registrar un visitante');
          return;
        }
        
        const eventId = this.events[0].id;
        const visitorData = {
          name: 'Visitante Prueba ' + Date.now(),
          email: `visitante.prueba.${Date.now()}@example.com`,
          phone: '809-123-4567',
          identification: 'TEST-12345'
        };
        
        console.log('Creando visitante de prueba para el evento:', eventId);
        console.log('Datos del visitante:', visitorData);
        
        const response = await this.registerVisitorForEvent({
          eventId,
          visitorData
        });
        
        console.log('Respuesta de creación:', response);
        this.apiResponse = response;
        alert('Visitante de prueba creado correctamente');
        
        // Recargar la lista de visitantes
        await this.fetchVisitors();
      } catch (error) {
        console.error('Error al crear visitante de prueba:', error);
        this.apiResponse = error.response?.data || error.message;
        alert('Error al crear visitante de prueba: ' + (error.response?.data?.message || error.message));
      }
    }
  },
  created() {
    // Cargar visitantes y eventos al crear el componente
    this.fetchVisitors({ limit: 100 });
    this.fetchEvents();
    
    // Agregar información de debug
    console.log('Visitors.vue creado - cargando datos iniciales');
  }
};
</script>

<style scoped>
.visitors-view {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  color: #512da8;
  margin-bottom: 10px;
}

.actions-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 20px 0;
  flex-wrap: wrap;
  gap: 10px;
}

.search-box input {
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 300px;
  font-size: 1rem;
}

.filters select {
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  background-color: white;
  min-width: 200px;
}

.admin-actions {
  display: flex;
  gap: 10px;
}

.btn {
  padding: 10px 15px;
  border-radius: 4px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background-color: #512da8;
  color: white;
  border: none;
}

.btn-primary:hover:not(:disabled) {
  background-color: #4527a0;
}

.btn-primary:disabled {
  background-color: #9e9e9e;
  cursor: not-allowed;
}

.debug-info {
  background-color: #f9f9f9;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 15px;
  margin: 20px 0;
  font-family: monospace;
  font-size: 0.9rem;
}

.debug-info pre {
  margin: 10px 0;
  overflow-x: auto;
  max-height: 200px;
  background-color: #eee;
  padding: 10px;
  border-radius: 4px;
}

.table-container {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #666;
}

.empty-state i {
  font-size: 3rem;
  color: #ddd;
  margin-bottom: 20px;
}

.empty-state p {
  margin-bottom: 20px;
  font-size: 1.1rem;
}

.visitors-table {
  width: 100%;
  border-collapse: collapse;
}

.visitors-table th {
  text-align: left;
  padding: 15px;
  background-color: #f5f5f5;
  color: #333;
  font-weight: 600;
}

.visitors-table td {
  padding: 15px;
  border-top: 1px solid #eee;
}

.status-badge {
  display: inline-block;
  padding: 5px 10px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
}

.status-checked {
  background-color: #e3fcef;
  color: #00b894;
}

.status-pending {
  background-color: #fff3cd;
  color: #fd9644;
}

.actions-cell {
  display: flex;
  gap: 5px;
}

.btn-icon {
  width: 36px;
  height: 36px;
  border-radius: 4px;
  border: none;
  background-color: #f5f5f5;
  color: #333;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-icon:hover {
  background-color: #e0e0e0;
}

.btn-icon.delete {
  color: #e74c3c;
}

.btn-icon.delete:hover {
  background-color: #fce8e6;
}

.last-event {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.event-title {
  font-weight: 500;
}

.event-meta {
  display: flex;
  gap: 8px;
  align-items: center;
  font-size: 0.85rem;
}

.event-type {
  padding: 2px 6px;
  border-radius: 12px;
  font-size: 0.75rem;
}

.event-type-cine {
  background-color: #e3f2fd;
  color: #0d6efd;
}

.event-type-exposición {
  background-color: #e3fcef;
  color: #00b894;
}

.event-type-charla {
  background-color: #fff3cd;
  color: #fd9644;
}

.event-type-taller {
  background-color: #f8d7da;
  color: #dc3545;
}

.event-type-concierto {
  background-color: #d8f5a2;
  color: #28a745;
}

.event-type-exhibición {
  background-color: #e2e3e5;
  color: #495057;
}

.event-type-otro {
  background-color: #f8f9fa;
  color: #6c757d;
}

.no-event, .no-interests {
  color: #aaa;
  font-style: italic;
  font-size: 0.9rem;
}

.interests-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.interest-tag {
  padding: 2px 8px;
  border-radius: 16px;
  font-size: 0.8rem;
  white-space: nowrap;
}

.interest-cine {
  background-color: #e3f2fd;
  color: #0d6efd;
}

.interest-exposición {
  background-color: #e3fcef;
  color: #00b894;
}

.interest-charla {
  background-color: #fff3cd;
  color: #fd9644;
}

.interest-taller {
  background-color: #f8d7da;
  color: #dc3545;
}

.interest-concierto {
  background-color: #d8f5a2;
  color: #28a745;
}

.interest-exhibición {
  background-color: #e2e3e5;
  color: #495057;
}

.interest-otro {
  background-color: #f8f9fa;
  color: #6c757d;
}

@media (max-width: 768px) {
  .actions-bar {
    flex-direction: column;
    align-items: stretch;
    gap: 15px;
  }
  
  .search-box input,
  .filters select {
    width: 100%;
  }
  
  .visitors-table {
    display: block;
    overflow-x: auto;
  }
}

.loading-overlay {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top: 4px solid #512da8;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  background-color: #fff3f3;
  border-left: 4px solid #e74c3c;
  padding: 15px;
  margin: 20px 0;
  border-radius: 4px;
}

.btn-retry {
  background-color: #e74c3c;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 10px;
}

.no-data {
  text-align: center;
  padding: 30px;
  color: #666;
  font-style: italic;
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

.modal-container {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.invitation-modal {
  max-width: 700px;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h2 {
  color: #333;
  margin: 0;
  font-size: 1.5rem;
}

.close-btn {
  background: none;
  border: none;
  color: #999;
  font-size: 1.5rem;
  cursor: pointer;
}

.modal-body {
  padding: 20px 0;
  max-height: 60vh;
  overflow-y: auto;
}

.modal-footer {
  padding-top: 20px;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.section-title {
  font-weight: 600;
  margin-bottom: 10px;
  color: #555;
}

.selected-visitors {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 20px;
}

.selected-visitor-chip {
  background-color: #f0f0f0;
  padding: 5px 10px;
  border-radius: 20px;
  font-size: 0.9rem;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #555;
}

.form-control {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.event-preview {
  margin-bottom: 20px;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 15px;
  background-color: #f9f9f9;
}

.event-preview h3 {
  margin-top: 0;
  font-size: 1.2rem;
  color: #333;
}

.event-details-preview {
  margin-top: 15px;
}

.email-preview {
  margin-bottom: 20px;
}

.email-preview h3 {
  margin-top: 0;
  font-size: 1.2rem;
  color: #333;
}

.email-template {
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
}

.email-header {
  padding: 10px 15px;
  background-color: #f5f5f5;
  border-bottom: 1px solid #ddd;
}

.email-subject {
  font-weight: 600;
}

.email-body {
  padding: 15px;
  background-color: white;
}

.email-event-highlight {
  margin: 15px 0;
  padding: 10px;
  background-color: #f5f5f5;
  border-left: 4px solid #F99D2A;
  font-weight: 500;
}

.email-code-highlight {
  display: inline-block;
  margin: 10px 0;
  padding: 10px 20px;
  background-color: #F99D2A;
  color: white;
  font-weight: 600;
  letter-spacing: 1px;
}
</style>
