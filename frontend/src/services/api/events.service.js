import apiService from './api.service';

/**
 * Servicio para gestionar los eventos
 */
class EventsService {
  /**
   * Obtiene la lista de eventos
   * @param {Object} params - Parámetros de filtrado y paginación
   * @returns {Promise} Promesa con lista de eventos
   */
  getEvents(params = {}) {
    return apiService.get('/events', params);
  }

  /**
   * Obtiene un evento por su ID
   * @param {number} eventId - ID del evento
   * @returns {Promise} Promesa con datos del evento
   */
  getEvent(eventId) {
    return apiService.get(`/events/${eventId}`);
  }

  /**
   * Crea un nuevo evento
   * @param {Object} eventData - Datos del evento
   * @returns {Promise} Promesa con el evento creado
   */
  createEvent(eventData) {
    return apiService.post('/events', eventData);
  }

  /**
   * Actualiza un evento existente
   * @param {number} eventId - ID del evento
   * @param {Object} eventData - Datos actualizados del evento
   * @returns {Promise} Promesa con el evento actualizado
   */
  updateEvent(eventId, eventData) {
    return apiService.put(`/events/${eventId}`, eventData);
  }

  /**
   * Elimina un evento
   * @param {number} eventId - ID del evento
   * @returns {Promise} Promesa de confirmación
   */
  deleteEvent(eventId) {
    return apiService.delete(`/events/${eventId}`);
  }

  /**
   * Obtiene los visitantes registrados en un evento
   * @param {number} eventId - ID del evento
   * @param {Object} params - Parámetros de filtrado y paginación
   * @returns {Promise} Promesa con lista de visitantes
   */
  getEventVisitors(eventId, params = {}) {
    return apiService.get(`/events/${eventId}/visitors`, params);
  }

  /**
   * Obtiene las estadísticas de un evento
   * @param {number} eventId - ID del evento
   * @returns {Promise} Promesa con estadísticas del evento
   */
  getEventStats(eventId) {
    return apiService.get(`/events/${eventId}/stats`);
  }

  /**
   * Publica o despublica un evento
   * @param {number} eventId - ID del evento
   * @param {boolean} isPublished - Estado de publicación
   * @returns {Promise} Promesa con el evento actualizado
   */
  setEventPublishStatus(eventId, isPublished) {
    return apiService.put(`/events/${eventId}/publish`, { is_published: isPublished });
  }

  /**
   * Obtiene los próximos eventos
   * @param {number} limit - Cantidad de eventos a obtener
   * @returns {Promise} Promesa con lista de próximos eventos
   */
  getUpcomingEvents(limit = 5) {
    return apiService.get('/events/upcoming', { limit });
  }
}

export default new EventsService(); 