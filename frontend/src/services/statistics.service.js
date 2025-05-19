import apiService from './api/api.service';
import eventBus from '@/utils/eventBus';

/**
 * Servicio para gestionar estadísticas y reportes
 */
class StatisticsService {
  /**
   * Obtiene estadísticas generales de visitantes
   * @param {Object} params - Parámetros de filtrado (fechas, eventos, etc)
   * @returns {Promise} Promesa con estadísticas
   */
  getVisitorStatistics(params = {}) {
    return apiService.get('/statistics/visitors', params);
  }

  /**
   * Obtiene estadísticas de un evento específico
   * @param {number} eventId - ID del evento
   * @param {Object} params - Parámetros adicionales
   * @returns {Promise} Promesa con estadísticas del evento
   */
  getEventStatistics(eventId, params = {}) {
    return apiService.get(`/statistics/events/${eventId}`, params);
  }

  /**
   * Obtiene estadísticas de asistencia por período
   * @param {Object} params - Parámetros de filtrado por fechas
   * @returns {Promise} Promesa con estadísticas de asistencia
   */
  getAttendanceByPeriod(params = {}) {
    return apiService.get('/statistics/attendance', params);
  }

  /**
   * Obtiene datos para dashboard en tiempo real
   * @param {Object} params - Parámetros de filtrado
   * @returns {Promise} Promesa con datos del dashboard
   */
  async getDashboardData(params = {}) {
    try {
      const data = await apiService.get('/statistics/dashboard', params);
      
      // Emitir evento con los datos actualizados para actualización en tiempo real
      eventBus.emit('dashboard-data-updated', data);
      
      return data;
    } catch (error) {
      console.error('Error al obtener datos del dashboard:', error);
      throw error;
    }
  }

  /**
   * Configura actualizaciones en tiempo real para estadísticas
   * @param {Function} callback - Función a ejecutar cuando se actualicen las estadísticas
   * @returns {Function} Función para cancelar la suscripción
   */
  subscribeToRealTimeUpdates(callback) {
    // Suscribirse a actualizaciones
    eventBus.on('dashboard-data-updated', callback);
    eventBus.on('visitor-registered', this.handleVisitorEvent);
    eventBus.on('visitor-checked-in', this.handleVisitorEvent);
    
    // Devolver función para cancelar suscripción
    return () => {
      eventBus.off('dashboard-data-updated', callback);
      eventBus.off('visitor-registered', this.handleVisitorEvent);
      eventBus.off('visitor-checked-in', this.handleVisitorEvent);
    };
  }

  /**
   * Maneja eventos de visitantes para actualizar estadísticas
   * @private
   * @param {Object} data - Datos del evento
   */
  handleVisitorEvent(data) {
    // Solicitar actualización de datos
    this.getDashboardData().catch(err => {
      console.error('Error al actualizar estadísticas:', err);
    });
  }

  /**
   * Exporta estadísticas a CSV
   * @param {string} reportType - Tipo de reporte a exportar
   * @param {Object} params - Parámetros de filtrado
   * @returns {Promise} Promesa con datos CSV
   */
  exportStatistics(reportType, params = {}) {
    return apiService.get(`/statistics/export/${reportType}`, {
      ...params,
      format: 'csv'
    });
  }
}

export default new StatisticsService();