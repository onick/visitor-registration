import apiService from './api.service';

/**
 * Servicio para gestionar kioscos
 */
class KiosksService {
  /**
   * Obtiene la lista de kioscos
   * @param {Object} params - Parámetros de filtrado y paginación
   * @returns {Promise} Promesa con lista de kioscos
   */
  getKiosks(params = {}) {
    return apiService.get('/kiosks', params);
  }

  /**
   * Obtiene un kiosco por su ID
   * @param {number} kioskId - ID del kiosco
   * @returns {Promise} Promesa con datos del kiosco
   */
  getKiosk(kioskId) {
    return apiService.get(`/kiosks/${kioskId}`);
  }

  /**
   * Crea un nuevo kiosco
   * @param {Object} kioskData - Datos del kiosco
   * @returns {Promise} Promesa con el kiosco creado
   */
  createKiosk(kioskData) {
    return apiService.post('/kiosks', kioskData);
  }

  /**
   * Actualiza un kiosco existente
   * @param {number} kioskId - ID del kiosco
   * @param {Object} kioskData - Datos actualizados del kiosco
   * @returns {Promise} Promesa con el kiosco actualizado
   */
  updateKiosk(kioskId, kioskData) {
    return apiService.put(`/kiosks/${kioskId}`, kioskData);
  }

  /**
   * Elimina un kiosco
   * @param {number} kioskId - ID del kiosco
   * @returns {Promise} Promesa de confirmación
   */
  deleteKiosk(kioskId) {
    return apiService.delete(`/kiosks/${kioskId}`);
  }

  /**
   * Obtiene la configuración de un kiosco
   * @param {number} kioskId - ID del kiosco
   * @returns {Promise} Promesa con la configuración del kiosco
   */
  getKioskConfig(kioskId) {
    return apiService.get(`/kiosks/${kioskId}/config`);
  }

  /**
   * Actualiza la configuración de un kiosco
   * @param {number} kioskId - ID del kiosco
   * @param {Object} configData - Datos de configuración
   * @returns {Promise} Promesa con la configuración actualizada
   */
  updateKioskConfig(kioskId, configData) {
    return apiService.put(`/kiosks/${kioskId}/config`, configData);
  }

  /**
   * Envía un latido (heartbeat) para reportar actividad de un kiosco
   * @param {number} kioskId - ID del kiosco
   * @param {Object} heartbeatData - Datos adicionales del heartbeat
   * @returns {Promise} Promesa con confirmación
   */
  sendKioskHeartbeat(kioskId, heartbeatData = {}) {
    return apiService.post(`/kiosks/${kioskId}/heartbeat`, heartbeatData);
  }

  /**
   * Obtiene los eventos asignados a un kiosco
   * @param {number} kioskId - ID del kiosco
   * @returns {Promise} Promesa con lista de eventos
   */
  getKioskEvents(kioskId) {
    return apiService.get(`/kiosks/${kioskId}/events`);
  }

  /**
   * Obtiene el estado de todos los kioscos
   * @returns {Promise} Promesa con estado de los kioscos
   */
  getKiosksStatus() {
    return apiService.get('/kiosks/status');
  }

  /**
   * Reinicia un kiosco remotamente
   * @param {number} kioskId - ID del kiosco
   * @returns {Promise} Promesa con confirmación
   */
  restartKiosk(kioskId) {
    return apiService.post(`/kiosks/${kioskId}/restart`);
  }
}

export default new KiosksService(); 