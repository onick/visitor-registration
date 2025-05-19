import apiService from './api.service';

/**
 * Servicio para gestionar usuarios del sistema
 */
class UsersService {
  /**
   * Obtiene lista de usuarios
   * @param {Object} params - Parámetros de filtrado y paginación
   * @returns {Promise} Promesa con lista de usuarios
   */
  getUsers(params = {}) {
    return apiService.get('/users', params);
  }

  /**
   * Obtiene un usuario por ID
   * @param {number} userId - ID del usuario
   * @returns {Promise} Promesa con datos del usuario
   */
  getUser(userId) {
    return apiService.get(`/users/${userId}`);
  }

  /**
   * Crea un nuevo usuario
   * @param {Object} userData - Datos del usuario
   * @returns {Promise} Promesa con el usuario creado
   */
  createUser(userData) {
    return apiService.post('/users', userData);
  }

  /**
   * Actualiza un usuario existente
   * @param {number} userId - ID del usuario
   * @param {Object} userData - Datos actualizados
   * @returns {Promise} Promesa con el usuario actualizado
   */
  updateUser(userId, userData) {
    return apiService.put(`/users/${userId}`, userData);
  }

  /**
   * Elimina un usuario
   * @param {number} userId - ID del usuario
   * @returns {Promise} Promesa de confirmación
   */
  deleteUser(userId) {
    return apiService.delete(`/users/${userId}`);
  }

  /**
   * Actualiza el estado activo/inactivo de un usuario
   * @param {number} userId - ID del usuario
   * @param {boolean} isActive - Estado activo
   * @returns {Promise} Promesa con el usuario actualizado
   */
  setUserActiveStatus(userId, isActive) {
    return apiService.patch(`/users/${userId}/status`, { is_active: isActive });
  }

  /**
   * Actualiza el rol de un usuario
   * @param {number} userId - ID del usuario
   * @param {string} role - Nuevo rol ('admin', 'staff')
   * @returns {Promise} Promesa con el usuario actualizado
   */
  updateUserRole(userId, role) {
    return apiService.patch(`/users/${userId}/role`, { role });
  }

  /**
   * Restablece la contraseña de un usuario (sólo admin)
   * @param {number} userId - ID del usuario
   * @returns {Promise} Promesa con token de restablecimiento
   */
  resetUserPassword(userId) {
    return apiService.post(`/users/${userId}/reset-password`);
  }

  /**
   * Obtiene el registro de actividad de un usuario
   * @param {number} userId - ID del usuario
   * @param {Object} params - Parámetros de filtrado
   * @returns {Promise} Promesa con registro de actividad
   */
  getUserActivityLog(userId, params = {}) {
    return apiService.get(`/users/${userId}/activity`, params);
  }
}

export default new UsersService(); 