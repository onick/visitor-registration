<template>
  <div class="data-table-wrapper">
    <!-- Barra superior con buscador y acciones -->
    <div class="data-table-header">
      <div class="search-box" v-if="showSearch">
        <input 
          type="text" 
          v-model="searchQuery" 
          :placeholder="searchPlaceholder" 
          class="search-input"
          @input="onSearch"
        >
        <button class="search-btn" @click="onSearch">
          <i class="fas fa-search"></i>
        </button>
      </div>
      
      <div class="table-actions">
        <slot name="actions"></slot>
      </div>
    </div>
    
    <!-- Tabla de datos -->
    <div class="table-container" :class="{ 'is-loading': loading }">
      <table class="data-table">
        <thead>
          <tr>
            <th v-for="column in columns" :key="column.field" :class="getColumnClass(column)">
              <div class="th-content" @click="sortBy(column)">
                {{ column.label }}
                <span v-if="column.sortable" class="sort-icon">
                  <i v-if="sortField === column.field" 
                     :class="[
                       'fas', 
                       sortDirection === 'asc' ? 'fa-sort-up' : 'fa-sort-down'
                     ]"></i>
                  <i v-else class="fas fa-sort"></i>
                </span>
              </div>
            </th>
            <th v-if="hasRowActions" class="actions-column">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <template v-if="processedItems.length">
            <tr v-for="(item, index) in processedItems" :key="getItemKey(item, index)">
              <td v-for="column in columns" :key="column.field" :class="getColumnClass(column)">
                <slot :name="`column-${column.field}`" :item="item" :value="getItemValue(item, column)">
                  {{ formatValue(getItemValue(item, column), column.format) }}
                </slot>
              </td>
              <td v-if="hasRowActions" class="actions-column">
                <div class="row-actions">
                  <slot name="row-actions" :item="item" :index="index"></slot>
                </div>
              </td>
            </tr>
          </template>
          <tr v-else-if="loading" class="loading-row">
            <td :colspan="columns.length + (hasRowActions ? 1 : 0)" class="loading-message">
              <div class="spinner">
                <i class="fas fa-spinner fa-spin"></i>
              </div>
              <span>Cargando datos...</span>
            </td>
          </tr>
          <tr v-else class="empty-row">
            <td :colspan="columns.length + (hasRowActions ? 1 : 0)" class="empty-message">
              <slot name="empty">
                <div class="no-data">
                  <i class="fas fa-inbox"></i>
                  <p>{{ emptyMessage }}</p>
                </div>
              </slot>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- Paginación -->
    <div v-if="showPagination" class="data-table-footer">
      <div class="pagination-info">
        Mostrando {{ paginationInfo.from }}-{{ paginationInfo.to }} de {{ paginationInfo.total }} registros
      </div>
      
      <div class="pagination-controls">
        <button 
          class="pagination-btn" 
          :disabled="currentPage === 1"
          @click="changePage(1)"
        >
          <i class="fas fa-angle-double-left"></i>
        </button>
        <button 
          class="pagination-btn" 
          :disabled="currentPage === 1"
          @click="changePage(currentPage - 1)"
        >
          <i class="fas fa-angle-left"></i>
        </button>
        
        <span class="page-indicator">
          {{ currentPage }} de {{ totalPages }}
        </span>
        
        <button 
          class="pagination-btn" 
          :disabled="currentPage === totalPages"
          @click="changePage(currentPage + 1)"
        >
          <i class="fas fa-angle-right"></i>
        </button>
        <button 
          class="pagination-btn" 
          :disabled="currentPage === totalPages"
          @click="changePage(totalPages)"
        >
          <i class="fas fa-angle-double-right"></i>
        </button>
      </div>
      
      <div class="page-size-selector">
        <label for="page-size">Por página:</label>
        <select id="page-size" v-model="pageSize" @change="onPageSizeChange">
          <option v-for="size in pageSizeOptions" :key="size" :value="size">{{ size }}</option>
        </select>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DataTable',
  props: {
    columns: {
      type: Array,
      required: true,
      /* 
      Example:
      [
        { field: 'id', label: 'ID', sortable: true },
        { field: 'name', label: 'Nombre', sortable: true },
        { field: 'email', label: 'Email', sortable: true },
        { 
          field: 'created_at', 
          label: 'Fecha', 
          sortable: true,
          format: 'date' 
        }
      ]
      */
    },
    items: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    },
    itemKey: {
      type: String,
      default: 'id'
    },
    showSearch: {
      type: Boolean,
      default: true
    },
    searchPlaceholder: {
      type: String,
      default: 'Buscar...'
    },
    showPagination: {
      type: Boolean,
      default: true
    },
    initialSort: {
      type: Object,
      default: () => ({ field: '', direction: 'asc' })
    },
    initialSearch: {
      type: String,
      default: ''
    },
    serverSideOptions: {
      type: Object,
      default: () => ({
        enabled: false,
        total: 0,
        currentPage: 1,
        pageSize: 10
      })
    },
    emptyMessage: {
      type: String,
      default: 'No hay datos para mostrar'
    },
    pageSizeOptions: {
      type: Array,
      default: () => [10, 25, 50, 100]
    }
  },
  data() {
    return {
      searchQuery: this.initialSearch,
      sortField: this.initialSort.field,
      sortDirection: this.initialSort.direction,
      currentPage: this.serverSideOptions.enabled ? this.serverSideOptions.currentPage : 1,
      pageSize: this.serverSideOptions.enabled ? this.serverSideOptions.pageSize : 10
    };
  },
  computed: {
    hasRowActions() {
      return !!this.$slots['row-actions'];
    },
    processedItems() {
      if (this.serverSideOptions.enabled) {
        return this.items;
      }
      
      let filteredItems = this.items;
      
      // Filtrado local
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        filteredItems = filteredItems.filter(item => {
          return this.columns.some(column => {
            const value = this.getItemValue(item, column);
            return value != null && String(value).toLowerCase().includes(query);
          });
        });
      }
      
      // Ordenamiento local
      if (this.sortField) {
        filteredItems = [...filteredItems].sort((a, b) => {
          const aValue = this.getItemValue(a, { field: this.sortField });
          const bValue = this.getItemValue(b, { field: this.sortField });
          
          if (aValue == null) return this.sortDirection === 'asc' ? -1 : 1;
          if (bValue == null) return this.sortDirection === 'asc' ? 1 : -1;
          
          if (aValue < bValue) return this.sortDirection === 'asc' ? -1 : 1;
          if (aValue > bValue) return this.sortDirection === 'asc' ? 1 : -1;
          return 0;
        });
      }
      
      // Paginación local
      const startIndex = (this.currentPage - 1) * this.pageSize;
      return filteredItems.slice(startIndex, startIndex + this.pageSize);
    },
    totalItems() {
      if (this.serverSideOptions.enabled) {
        return this.serverSideOptions.total;
      }
      
      if (!this.searchQuery) {
        return this.items.length;
      }
      
      // Contar elementos filtrados
      const query = this.searchQuery.toLowerCase();
      return this.items.filter(item => {
        return this.columns.some(column => {
          const value = this.getItemValue(item, column);
          return value != null && String(value).toLowerCase().includes(query);
        });
      }).length;
    },
    totalPages() {
      return Math.max(1, Math.ceil(this.totalItems / this.pageSize));
    },
    paginationInfo() {
      const from = this.totalItems === 0 ? 0 : (this.currentPage - 1) * this.pageSize + 1;
      const to = Math.min(this.currentPage * this.pageSize, this.totalItems);
      
      return {
        from,
        to,
        total: this.totalItems
      };
    }
  },
  methods: {
    getItemValue(item, column) {
      if (!column.field) return null;
      
      // Soporte para campos anidados como 'user.name'
      return column.field.split('.').reduce((obj, key) => {
        return obj && obj[key] !== undefined ? obj[key] : null;
      }, item);
    },
    formatValue(value, format) {
      if (value == null) return '';
      
      switch (format) {
        case 'date':
          return new Date(value).toLocaleDateString('es-ES');
        case 'datetime':
          return new Date(value).toLocaleString('es-ES');
        case 'currency':
          return typeof value === 'number' 
            ? value.toLocaleString('es-ES', { style: 'currency', currency: 'DOP' })
            : value;
        case 'boolean':
          return value ? 'Sí' : 'No';
        default:
          return value;
      }
    },
    getItemKey(item, index) {
      return this.itemKey && item[this.itemKey] ? item[this.itemKey] : index;
    },
    getColumnClass(column) {
      return {
        sortable: column.sortable,
        sorted: this.sortField === column.field,
        [column.field]: true,
        [column.class]: !!column.class
      };
    },
    sortBy(column) {
      if (!column.sortable) return;
      
      // Si ya estamos ordenando por esta columna, cambiamos dirección
      if (this.sortField === column.field) {
        this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
      } else {
        this.sortField = column.field;
        this.sortDirection = 'asc';
      }
      
      if (this.serverSideOptions.enabled) {
        this.$emit('sort', { field: this.sortField, direction: this.sortDirection });
      }
      
      // Restablecer la página actual a 1 cuando cambiamos el ordenamiento
      if (this.currentPage !== 1) {
        this.currentPage = 1;
      }
    },
    onSearch() {
      if (this.serverSideOptions.enabled) {
        this.$emit('search', this.searchQuery);
      }
      
      // Restablecer la página actual a 1 cuando realizamos una búsqueda
      this.currentPage = 1;
    },
    changePage(page) {
      if (page < 1 || page > this.totalPages) return;
      
      this.currentPage = page;
      
      if (this.serverSideOptions.enabled) {
        this.$emit('page-change', this.currentPage);
      }
    },
    onPageSizeChange() {
      // Ajustar la página actual para evitar páginas vacías
      const maxPage = Math.ceil(this.totalItems / this.pageSize);
      if (this.currentPage > maxPage) {
        this.currentPage = maxPage || 1;
      }
      
      if (this.serverSideOptions.enabled) {
        this.$emit('page-size-change', this.pageSize);
      }
    }
  },
  watch: {
    serverSideOptions: {
      deep: true,
      handler(newValue) {
        if (newValue.enabled) {
          this.currentPage = newValue.currentPage;
          this.pageSize = newValue.pageSize;
        }
      }
    }
  }
};
</script>

<style scoped>
.data-table-wrapper {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.data-table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
}

.search-box {
  display: flex;
  align-items: center;
  width: 300px;
  position: relative;
}

.search-input {
  width: 100%;
  padding: 10px 40px 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.search-input:focus {
  border-color: #512da8;
  outline: none;
}

.search-btn {
  position: absolute;
  right: 0;
  top: 0;
  height: 100%;
  width: 40px;
  background: none;
  border: none;
  color: #666;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.table-actions {
  display: flex;
  gap: 10px;
}

.table-container {
  width: 100%;
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th, .data-table td {
  padding: 12px 20px;
  text-align: left;
  border-bottom: 1px solid #eee;
  vertical-align: middle;
}

.data-table th {
  color: #666;
  font-weight: 600;
  font-size: 13px;
  background-color: #f9f9f9;
  white-space: nowrap;
  user-select: none;
}

.data-table th.sortable {
  cursor: pointer;
}

.th-content {
  display: flex;
  align-items: center;
}

.sort-icon {
  margin-left: 5px;
  color: #aaa;
}

.data-table th.sorted .sort-icon {
  color: #512da8;
}

.data-table td {
  font-size: 14px;
  color: #333;
}

.actions-column {
  width: 120px;
  text-align: center;
  white-space: nowrap;
}

.row-actions {
  display: flex;
  justify-content: center;
  gap: 8px;
}

.loading-row td, .empty-row td {
  padding: 30px;
  text-align: center;
  color: #666;
}

.loading-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.spinner {
  font-size: 24px;
  color: #512da8;
}

.no-data {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.no-data i {
  font-size: 32px;
  color: #ddd;
}

.data-table-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-top: 1px solid #eee;
}

.pagination-info {
  font-size: 13px;
  color: #666;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 5px;
}

.pagination-btn {
  width: 32px;
  height: 32px;
  border-radius: 4px;
  border: 1px solid #ddd;
  background-color: #fff;
  color: #666;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.pagination-btn:hover:not(:disabled) {
  background-color: #f5f5f5;
  border-color: #ccc;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-indicator {
  margin: 0 10px;
  font-size: 13px;
  color: #666;
}

.page-size-selector {
  display: flex;
  align-items: center;
  gap: 10px;
}

.page-size-selector label {
  font-size: 13px;
  color: #666;
}

.page-size-selector select {
  padding: 5px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #fff;
  color: #333;
  font-size: 13px;
}

.is-loading {
  position: relative;
  min-height: 200px;
}

@media (max-width: 768px) {
  .data-table-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .search-box {
    width: 100%;
  }
  
  .data-table-footer {
    flex-direction: column;
    gap: 15px;
    align-items: center;
  }
  
  .pagination-info {
    order: 3;
  }
  
  .page-size-selector {
    order: 2;
  }
  
  .pagination-controls {
    order: 1;
    width: 100%;
    justify-content: center;
  }
}
</style> 