<template>
  <div class="visitor-filter">
    <div class="filter-header">
      <h3>Filtros</h3>
      <button class="btn-clear" @click="clearFilters" v-if="hasActiveFilters">
        <i class="fas fa-times"></i> Limpiar filtros
      </button>
    </div>
    
    <div class="filter-body">
      <div class="filter-group">
        <label>Buscar</label>
        <div class="search-input">
          <i class="fas fa-search"></i>
          <input 
            type="text" 
            v-model="filters.searchTerm" 
            placeholder="Nombre, email o teléfono..."
            @input="applyFilters"
          />
          <button v-if="filters.searchTerm" class="clear-search" @click="clearSearch">
            <i class="fas fa-times"></i>
          </button>
        </div>
      </div>
      
      <div class="filter-group">
        <label>Evento</label>
        <select v-model="filters.eventId" @change="applyFilters">
          <option value="">Todos los eventos</option>
          <option v-for="event in events" :key="event.id" :value="event.id">
            {{ event.name || event.title }} (ID: {{ event.id }})
          </option>
        </select>
      </div>
      
      <div class="filter-group">
        <label>Estado</label>
        <select v-model="filters.status" @change="applyFilters">
          <option value="">Todos</option>
          <option value="registered">Solo registrados</option>
          <option value="checked-in">Con check-in</option>
          <option value="pending">Pendientes de check-in</option>
        </select>
      </div>
      
      <div class="filter-group">
        <label>Interés</label>
        <select v-model="filters.interest" @change="applyFilters">
          <option value="">Todos los intereses</option>
          <option value="cine">Cine 🎬</option>
          <option value="exposición">Exposición 🖼️</option>
          <option value="charla">Charla 🗣️</option>
          <option value="taller">Taller 🔨</option>
          <option value="concierto">Concierto 🎵</option>
          <option value="exhibición">Exhibición 🏺</option>
          <option value="otro">Otro 📌</option>
        </select>
      </div>
      
      <div class="filter-group">
        <label>Fecha de registro</label>
        <div class="date-range">
          <div class="date-input">
            <label>Desde</label>
            <input 
              type="date" 
              v-model="filters.dateFrom" 
              @change="applyFilters"
            />
          </div>
          <div class="date-input">
            <label>Hasta</label>
            <input 
              type="date" 
              v-model="filters.dateTo" 
              @change="applyFilters"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'VisitorFilter',
  props: {
    events: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      filters: {
        searchTerm: '',
        eventId: '',
        status: '',
        dateFrom: '',
        dateTo: '',
        interest: ''
      }
    };
  },
  computed: {
    hasActiveFilters() {
      return (
        this.filters.searchTerm || 
        this.filters.eventId || 
        this.filters.status || 
        this.filters.dateFrom || 
        this.filters.dateTo
      );
    }
  },
  methods: {
    applyFilters() {
      // Enviamos el evento con los filtros
      this.$emit('filter-change', { ...this.filters });
      
      // Registramos en consola los filtros aplicados para debug
      console.log('Filtros aplicados:', this.filters);
    },
    clearFilters() {
      this.filters = {
        searchTerm: '',
        eventId: '',
        status: '',
        dateFrom: '',
        dateTo: '',
        interest: ''
      };
      this.applyFilters();
    },
    clearSearch() {
      this.filters.searchTerm = '';
      this.applyFilters();
    }
  }
};
</script>

<style scoped>
.visitor-filter {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
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
  color: #333;
}

.btn-clear {
  background: none;
  border: none;
  color: #dc3545;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
}

.filter-body {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 16px;
}

.filter-group {
  margin-bottom: 12px;
}

.filter-group label {
  display: block;
  margin-bottom: 6px;
  font-size: 14px;
  color: #555;
}

.search-input {
  position: relative;
  display: flex;
  align-items: center;
}

.search-input i {
  position: absolute;
  left: 10px;
  color: #aaa;
}

.search-input input {
  padding: 8px 30px 8px 30px;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 100%;
  font-size: 14px;
}

.clear-search {
  position: absolute;
  right: 10px;
  background: none;
  border: none;
  color: #aaa;
  cursor: pointer;
}

select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background-color: white;
}

.date-range {
  display: flex;
  gap: 10px;
}

.date-input {
  flex: 1;
}

.date-input label {
  font-size: 12px;
  margin-bottom: 4px;
}

.date-input input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

@media (max-width: 768px) {
  .filter-body {
    grid-template-columns: 1fr;
  }
  
  .date-range {
    flex-direction: column;
    gap: 8px;
  }
}
</style>