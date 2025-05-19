<template>
  <div class="export-dialog">
    <div class="header">
      <h3>Exportar Datos del Evento</h3>
      <button @click="$emit('close')" class="close-btn">&times;</button>
    </div>
    
    <div class="content">
      <!-- Formato de exportación -->
      <div class="form-group">
        <label>Formato de exportación</label>
        <div class="format-options">
          <label class="radio-option">
            <input 
              type="radio" 
              value="csv" 
              v-model="exportFormat"
            >
            <span>CSV</span>
          </label>
          <label class="radio-option">
            <input 
              type="radio" 
              value="excel" 
              v-model="exportFormat"
            >
            <span>Excel</span>
          </label>
        </div>
      </div>

      <!-- Filtros de fecha -->
      <div class="form-group">
        <label>Rango de fechas</label>
        <div class="date-range">
          <input 
            type="date" 
            v-model="filters.startDate"
            class="date-input"
            placeholder="Fecha inicio"
          >
          <span class="separator">a</span>
          <input 
            type="date" 
            v-model="filters.endDate"
            class="date-input"
            placeholder="Fecha fin"
          >
        </div>
      </div>

      <!-- Filtro de check-in -->
      <div class="form-group">
        <label>Estado de check-in</label>
        <select v-model="filters.checkedIn" class="form-select">
          <option value="">Todos</option>
          <option value="true">Con check-in</option>
          <option value="false">Sin check-in</option>
        </select>
      </div>

      <!-- Búsqueda -->
      <div class="form-group">
        <label>Buscar visitante</label>
        <input 
          type="text" 
          v-model="filters.search"
          class="form-input"
          placeholder="Por nombre, email o código"
        >
      </div>

      <!-- Ordenamiento -->
      <div class="form-group">
        <label>Ordenar por</label>
        <div class="sort-options">
          <select v-model="filters.sortBy" class="form-select">
            <option value="created_at">Fecha de registro</option>
            <option value="name">Nombre</option>
            <option value="email">Email</option>
            <option value="registration_code">Código</option>
          </select>
          <select v-model="filters.sortOrder" class="form-select">
            <option value="desc">Descendente</option>
            <option value="asc">Ascendente</option>
          </select>
        </div>
      </div>
    </div>

    <div class="footer">
      <button @click="$emit('close')" class="btn btn-secondary">
        Cancelar
      </button>
      <button @click="exportData" class="btn btn-primary" :disabled="isExporting">
        <span v-if="!isExporting">Exportar</span>
        <span v-else>Exportando...</span>
      </button>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useStore } from 'vuex'
import NotificationService from '@/services/notificationService'

export default {
  name: 'ExportDialog',
  props: {
    eventId: {
      type: Number,
      required: true
    }
  },
  setup(props, { emit }) {
    const store = useStore()
    
    const exportFormat = ref('csv')
    const isExporting = ref(false)
    const filters = ref({
      startDate: '',
      endDate: '',
      checkedIn: '',
      search: '',
      sortBy: 'created_at',
      sortOrder: 'desc'
    })

    const exportData = async () => {
      isExporting.value = true
      
      const loadingToast = NotificationService.loading('Preparando exportación...')
      
      try {
        // Construir parámetros de query
        const params = new URLSearchParams({
          format: exportFormat.value,
          ...Object.fromEntries(
            Object.entries(filters.value).filter(([_, value]) => value !== '')
          )
        })

        // Obtener token de autenticación
        const token = store.state.auth.token || 'token-de-ejemplo'

        const response = await fetch(
          `${process.env.VUE_APP_API_URL}/events/${props.eventId}/export?${params}`,
          {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          }
        )

        if (!response.ok) {
          const error = await response.json()
          throw new Error(error.error || 'Error al exportar datos')
        }

        // Obtener el blob del archivo
        const blob = await response.blob()
        
        // Obtener el nombre del archivo del header Content-Disposition
        const contentDisposition = response.headers.get('content-disposition')
        const filename = contentDisposition
          ? contentDisposition.split('filename=')[1].replace(/"/g, '')
          : `export_${props.eventId}_${Date.now()}.${exportFormat.value}`

        // Crear un link temporal para descargar
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = filename
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)

        NotificationService.dismiss(loadingToast)
        NotificationService.success('Datos exportados exitosamente')
        emit('close')
      } catch (error) {
        console.error('Error al exportar:', error)
        NotificationService.dismiss(loadingToast)
        NotificationService.error(error.message || 'Error al exportar datos')
      } finally {
        isExporting.value = false
      }
    }

    return {
      exportFormat,
      isExporting,
      filters,
      exportData
    }
  }
}
</script>

<style scoped>
.export-dialog {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #6b7280;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.close-btn:hover {
  background-color: #f3f4f6;
}

.content {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #374151;
}

.format-options {
  display: flex;
  gap: 1rem;
}

.radio-option {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.radio-option input[type="radio"] {
  margin-right: 0.5rem;
  cursor: pointer;
}

.radio-option span {
  color: #4b5563;
}

.date-range {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.date-input,
.form-input,
.form-select {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.date-input:focus,
.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: #F99D2A;
  box-shadow: 0 0 0 3px rgba(249, 157, 42, 0.1);
}

.separator {
  color: #6b7280;
  font-weight: 500;
}

.sort-options {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 0.5rem;
}

.footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1.5rem;
  border-top: 1px solid #e5e7eb;
  background-color: #f9fafb;
  border-radius: 0 0 8px 8px;
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-weight: 500;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-secondary {
  background-color: white;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-secondary:hover {
  background-color: #f9fafb;
}

.btn-primary {
  background-color: #F99D2A;
  color: white;
}

.btn-primary:hover {
  background-color: #e88e1f;
}

.btn-primary:disabled {
  background-color: #fbbf24;
  cursor: not-allowed;
}
</style>
