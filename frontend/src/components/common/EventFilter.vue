<template>
  <div class="event-filter">
    <div class="filter-header">
      <h3>Filtros</h3>
      <button class="clear-btn" @click="clearFilters" v-if="hasActiveFilters">
        <i class="fas fa-times"></i> Limpiar
      </button>
    </div>
    
    <div class="filter-section">
      <label>Buscar por nombre:</label>
      <input 
        type="text" 
        v-model="filters.name" 
        placeholder="Nombre del evento"
        @input="applyFilters"
      />
    </div>
    
    <div class="filter-section">
      <label>Estado:</label>
      <select v-model="filters.status" @change="applyFilters">
        <option value="">Todos</option>
        <option value="active">Activos</option>
        <option value="upcoming">Próximos</option>
        <option value="past">Pasados</option>
      </select>
    </div>
    
    <div class="filter-section">
      <label>Fecha:</label>
      <div class="date-range">
        <input 
          type="date" 
          v-model="filters.startDate" 
          placeholder="Desde"
          @change="applyFilters"
        />
        <input 
          type="date" 
          v-model="filters.endDate" 
          placeholder="Hasta"
          @change="applyFilters"
        />
      </div>
    </div>
    
    <div class="filter-section">
      <label>Ordenar por:</label>
      <select v-model="filters.sortBy" @change="applyFilters">
        <option value="date_asc">Fecha (ascendente)</option>
        <option value="date_desc">Fecha (descendente)</option>
        <option value="name_asc">Nombre (A-Z)</option>
        <option value="name_desc">Nombre (Z-A)</option>
        <option value="visitors_desc">Más visitantes</option>
      </select>
    </div>
    
    <div class="filter-actions">
      <button class="apply-btn" @click="applyFilters">
        <i class="fas fa-filter"></i> Aplicar filtros
      </button>
    </div>
  </div>
</template>

<script>
import eventBus from '@/utils/eventBus';

export default {
  name: 'EventFilter',
  data() {
    return {
      filters: {
        name: '',
        status: '',
        startDate: '',
        endDate: '',
        sortBy: 'date_desc'
      }
    };
  },
  computed: {
    hasActiveFilters() {
      return (
        this.filters.name !== '' ||
        this.filters.status !== '' ||
        this.filters.startDate !== '' ||
        this.filters.endDate !== ''
      );
    }
  },
  methods: {
    applyFilters() {
      // Emitir evento con los filtros actualizados
      this.$emit('filter-change', { ...this.filters });
      
      // También emitir a través del eventBus para componentes no relacionados directamente
      eventBus.emit('event-filters-changed', { ...this.filters });
    },
    clearFilters() {
      this.filters = {
        name: '',
        status: '',
        startDate: '',
        endDate: '',
        sortBy: 'date_desc'
      };
      this.applyFilters();
    }
  }
};
</script>

<style scoped>
.event-filter {
  background-color: #fff;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.filter-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.clear-btn {
  background: none;
  border: none;
  color: #f56c6c;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
}

.clear-btn i {
  margin-right: 4px;
}

.filter-section {
  margin-bottom: 16px;
}

.filter-section label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #606266;
}

input[type="text"],
select,
input[type="date"] {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.2s;
}

input[type="text"]:focus,
select:focus,
input[type="date"]:focus {
  outline: none;
  border-color: #409eff;
}

.date-range {
  display: flex;
  gap: 8px;
}

.date-range input {
  flex: 1;
}

.filter-actions {
  margin-top: 20px;
}

.apply-btn {
  width: 100%;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 10px;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: background-color 0.2s;
}

.apply-btn:hover {
  background-color: #66b1ff;
}

.apply-btn i {
  margin-right: 8px;
}
</style>