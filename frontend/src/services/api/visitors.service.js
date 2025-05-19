import apiService from './api.service';

/**
 * Servicio para gestionar visitantes
 */
class VisitorsService {
  /**
   * Obtiene la lista de visitantes
   * @param {Object} params - Parámetros de filtrado y paginación
   * @returns {Promise} Promesa con lista de visitantes
   */
  getVisitors(params = {}) {
    return apiService.get('/visitors', params);
  }

  /**
   * Obtiene un visitante por su ID
   * @param {number} visitorId - ID del visitante
   * @returns {Promise} Promesa con datos del visitante
   */
  getVisitor(visitorId) {
    return apiService.get(`/visitors/${visitorId}`);
  }

  /**
   * Crea un nuevo visitante
   * @param {Object} visitorData - Datos del visitante
   * @returns {Promise} Promesa con el visitante creado
   */
  createVisitor(visitorData) {
    return apiService.post('/visitors', visitorData);
  }

  /**
   * Actualiza un visitante existente
   * @param {number} visitorId - ID del visitante
   * @param {Object} visitorData - Datos actualizados del visitante
   * @returns {Promise} Promesa con el visitante actualizado
   */
  updateVisitor(visitorId, visitorData) {
    return apiService.put(`/visitors/${visitorId}`, visitorData);
  }

  /**
   * Elimina un visitante
   * @param {number} visitorId - ID del visitante
   * @returns {Promise} Promesa de confirmación
   */
  deleteVisitor(visitorId) {
    return apiService.delete(`/visitors/${visitorId}`);
  }

  /**
   * Registra un visitante en un evento
   * @param {number} visitorId - ID del visitante
   * @param {number} eventId - ID del evento
   * @returns {Promise} Promesa con confirmación del registro
   */
  registerVisitorForEvent(visitorId, eventId) {
    return apiService.post(`/visitors/${visitorId}/register/${eventId}`);
  }

  /**
   * Registra el check-in de un visitante en un evento
   * @param {number} visitorId - ID del visitante
   * @param {number} eventId - ID del evento
   * @returns {Promise} Promesa con confirmación del check-in
   */
  checkInVisitor(visitorId, eventId) {
    return apiService.post(`/visitors/${visitorId}/check-in/${eventId}`);
  }

  /**
   * Obtiene estadísticas de visitantes
   * @param {Object} params - Parámetros de filtrado (fechas, etc)
   * @returns {Promise} Promesa con estadísticas
   */
  getVisitorStats(params = {}) {
    return apiService.get('/visitors/statistics', params);
  }

  /**
   * Busca visitantes por nombre, email o teléfono
   * @param {string} query - Texto de búsqueda
   * @returns {Promise} Promesa con lista de visitantes
   */
  searchVisitors(query) {
    return apiService.get('/visitors/search', { query });
  }

  /**
   * Obtiene los eventos a los que ha asistido un visitante
   * @param {number} visitorId - ID del visitante
   * @returns {Promise} Promesa con lista de eventos
   */
  getVisitorEvents(visitorId) {
    return apiService.get(`/visitors/${visitorId}/events`);
  }
}

export default new VisitorsService(); 