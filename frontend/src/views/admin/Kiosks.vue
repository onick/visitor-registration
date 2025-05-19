<template>
  <div class="kiosks-view">
    <h1>Gestión de Quioscos</h1>
    <p>Administración de los dos quioscos de registro de visitantes</p>
    
    <div class="actions-bar">
      <div class="search-box">
        <input type="text" placeholder="Buscar quioscos..." v-model="searchTerm">
      </div>
      <button class="btn btn-primary" @click="loadKiosks">
        <i class="fas fa-sync"></i> Actualizar
      </button>
    </div>
    
    <div v-if="loading" class="loading-state">
      <i class="fas fa-circle-notch fa-spin"></i>
      <p>Cargando kioscos...</p>
    </div>
    
    <div v-else class="kiosks-grid">
      <div v-for="kiosk in filteredKiosks" :key="kiosk.id" class="kiosk-card" :class="{'kiosk-inactive': !kiosk.is_active}">
        <div class="kiosk-header">
          <h3>{{ kiosk.name }}</h3>
          <div class="status-indicator" :class="kiosk.is_online ? 'status-active' : 'status-inactive'"></div>
        </div>
        <div class="kiosk-body">
          <p><strong>Ubicación:</strong> {{ kiosk.location }}</p>
          <p><strong>Modo:</strong> {{ kiosk.mode }}</p>
          <p><strong>IP:</strong> {{ kiosk.ipAddress }}</p>
          <p><strong>Último acceso:</strong> {{ formatDate(kiosk.lastActivity) }}</p>
          <div class="kiosk-stats">
            <div class="stat-box">
              <span class="stat-value">{{ kiosk.registrationCount }}</span>
              <span class="stat-label">Registros</span>
            </div>
            <div class="stat-box">
              <span class="stat-value">{{ kiosk.checkInCount }}</span>
              <span class="stat-label">Check-ins</span>
            </div>
          </div>
        </div>
        <div class="kiosk-footer">
          <button 
            class="btn btn-sm" 
            :class="kiosk.is_active ? 'btn-danger' : 'btn-success'"
            @click="toggleKioskStatus(kiosk)"
          >
            {{ kiosk.is_active ? 'Desactivar' : 'Activar' }}
          </button>
          <button 
            class="btn btn-sm btn-secondary"
            @click="restartKiosk(kiosk)"
          >
            Reiniciar
          </button>
          <button 
            class="btn btn-sm btn-info"
            @click="configureKiosk(kiosk)"
          >
            Configurar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'KiosksList',
  data() {
    return {
      searchTerm: '',
      kiosks: [],
      loading: true,
      showConfigModal: false,
      selectedKiosk: null
    };
  },
  computed: {
    filteredKiosks() {
      if (!this.searchTerm) return this.kiosks;
      
      const term = this.searchTerm.toLowerCase();
      return this.kiosks.filter(kiosk => 
        kiosk.name.toLowerCase().includes(term) ||
        kiosk.location.toLowerCase().includes(term) ||
        kiosk.mode.toLowerCase().includes(term) ||
        (kiosk.ipAddress && kiosk.ipAddress.includes(term))
      );
    }
  },
  mounted() {
    this.loadKiosks();
  },
  methods: {
    async loadKiosks() {
      this.loading = true;
      
      // Datos por defecto mientras se implementa el backend completo
      this.kiosks = [
        {
          id: 1,
          name: 'Kiosco Entrada Principal',
          location: 'Entrada Principal',
          mode: 'Registro y Check-in',
          ipAddress: '192.168.1.101',
          is_active: true,
          lastActivity: new Date().toISOString(),
          registrationCount: 0,
          checkInCount: 0,
          is_online: true
        },
        {
          id: 2,
          name: 'Kiosco Sala VR',
          location: 'Sala de Realidad Virtual',
          mode: 'Registro y Check-in',
          ipAddress: '192.168.1.102',
          is_active: true,
          lastActivity: new Date().toISOString(),
          registrationCount: 0,
          checkInCount: 0,
          is_online: true
        }
      ];
      
      // Intentar cargar desde el backend
      try {
        const response = await axios.get('/kiosks/');
        if (response.data && response.data.length > 0) {
          this.kiosks = response.data.map(kiosk => ({
            ...kiosk,
            mode: 'Registro y Check-in',
            ipAddress: `192.168.1.${100 + kiosk.id}`,
            registrationCount: 0,
            checkInCount: 0,
            is_online: this.isKioskOnline(kiosk.last_heartbeat)
          }));
        }
      } catch (error) {
        console.log('Usando datos por defecto de kioscos');
      } finally {
        this.loading = false;
      }
    },
    
    isKioskOnline(lastHeartbeat) {
      if (!lastHeartbeat) return false;
      const lastTime = new Date(lastHeartbeat);
      const now = new Date();
      const diffMinutes = (now - lastTime) / (1000 * 60);
      return diffMinutes < 5; // Considera online si reportó en los últimos 5 minutos
    },
    
    async toggleKioskStatus(kiosk) {
      try {
        const newStatus = !kiosk.is_active;
        const response = await axios.put(`/kiosks/${kiosk.id}`, {
          is_active: newStatus
        });
        
        if (response.data) {
          kiosk.is_active = newStatus;
          this.$store.dispatch('showNotification', {
            message: `Kiosco ${newStatus ? 'activado' : 'desactivado'} exitosamente`,
            type: 'success'
          });
        }
      } catch (error) {
        console.error('Error al cambiar estado del kiosco:', error);
        this.$store.dispatch('showNotification', {
          message: 'Error al cambiar el estado del kiosco',
          type: 'error'
        });
      }
    },
    
    async restartKiosk(kiosk) {
      try {
        // Simular reinicio del kiosco
        this.$store.dispatch('showNotification', {
          message: `Reiniciando ${kiosk.name}...`,
          type: 'info'
        });
        
        // En producción, esto enviaría una señal real al kiosco
        setTimeout(() => {
          this.$store.dispatch('showNotification', {
            message: `${kiosk.name} reiniciado exitosamente`,
            type: 'success'
          });
        }, 2000);
      } catch (error) {
        console.error('Error al reiniciar kiosco:', error);
        this.$store.dispatch('showNotification', {
          message: 'Error al reiniciar el kiosco',
          type: 'error'
        });
      }
    },
    
    configureKiosk(kiosk) {
      this.selectedKiosk = { ...kiosk };
      this.showConfigModal = true;
    },
    
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString('es-ES', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    }
  }
};
</script>

<style scoped>
.kiosks-view {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  color: var(--color-dark);
  margin-bottom: 10px;
}

p {
  color: var(--color-text-light);
  margin-bottom: 20px;
}

.actions-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 20px 0;
}

.search-box input {
  padding: 10px 15px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  width: 300px;
  font-size: 1rem;
  background-color: var(--color-background-light);
}

.search-box input:focus {
  outline: none;
  border-color: var(--color-secondary);
}

.btn {
  padding: 10px 15px;
  border-radius: var(--border-radius);
  font-size: 1rem;
  cursor: pointer;
  border: none;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: all 0.2s;
}

.btn-sm {
  padding: 7px 12px;
  font-size: 0.85rem;
}

.btn-primary {
  background-color: var(--color-primary);
  color: white;
}

.btn-primary:hover {
  background-color: var(--color-primary-dark);
}

.btn-secondary {
  background-color: var(--color-secondary);
  color: white;
}

.btn-secondary:hover {
  background-color: var(--color-secondary-dark);
}

.btn-info {
  background-color: var(--color-info);
  color: white;
}

.btn-info:hover {
  background-color: var(--color-secondary-dark);
}

.btn-success {
  background-color: var(--color-success);
  color: white;
}

.btn-danger {
  background-color: var(--color-danger);
  color: white;
}

.kiosks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.kiosk-card {
  background-color: white;
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  transition: all 0.3s ease;
}

.kiosk-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-lg);
}

.kiosk-inactive {
  opacity: 0.7;
}

.kiosk-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background-color: var(--color-background-light);
  border-bottom: 1px solid var(--border-color);
}

.kiosk-header h3 {
  margin: 0;
  color: var(--color-dark);
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.status-active {
  background-color: var(--color-success);
  box-shadow: 0 0 0 2px rgba(40, 167, 69, 0.2);
}

.status-inactive {
  background-color: var(--color-danger);
  box-shadow: 0 0 0 2px rgba(220, 53, 69, 0.2);
}

.kiosk-body {
  padding: 15px;
}

.kiosk-body p {
  margin: 10px 0;
  color: var(--color-text);
}

.kiosk-body p strong {
  color: var(--color-dark);
}

.kiosk-stats {
  display: flex;
  justify-content: space-between;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid var(--border-color);
}

.stat-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--color-primary);
}

.stat-label {
  font-size: 0.8rem;
  color: var(--color-text-light);
}

.kiosk-footer {
  display: flex;
  justify-content: space-between;
  padding: 15px;
  background-color: var(--color-background-light);
  border-top: 1px solid var(--border-color);
  gap: 8px;
}

@media (max-width: 768px) {
  .actions-bar {
    flex-direction: column;
    align-items: stretch;
    gap: 15px;
  }
  
  .search-box input {
    width: 100%;
  }
  
  .kiosk-footer {
    flex-direction: column;
    gap: 10px;
  }
  
  .kiosk-footer button {
    width: 100%;
  }
}

.loading-state {
  text-align: center;
  padding: 40px;
  color: var(--color-text-light);
}

.loading-state i {
  font-size: 48px;
  margin-bottom: 10px;
  opacity: 0.7;
  color: var(--color-secondary);
}
</style> 