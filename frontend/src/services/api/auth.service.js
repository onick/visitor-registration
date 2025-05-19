import apiService from './api.service';

/**
 * Servicio para gestionar la autenticación
 */
class AuthService {
  /**
   * Inicia sesión de usuario
   * @param {Object} credentials - Credenciales {username, password}
   * @returns {Promise} Promesa con el token y datos del usuario
   */
  login(credentials) {
    return apiService.post('/auth/login', credentials);
  }

  /**
   * Cierra la sesión del usuario
   * @returns {Promise} Promesa de confirmación
   */
  logout() {
    apiService.removeAuthHeader();
    return Promise.resolve();
  }

  /**
   * Obtiene información del usuario actual
   * @returns {Promise} Promesa con datos del usuario
   */
  getCurrentUser() {
    return apiService.get('/auth/me');
  }

  /**
   * Refresca el token de acceso
   * @param {string} refreshToken - Token de refresco
   * @returns {Promise} Promesa con el nuevo token
   */
  refreshToken(refreshToken) {
    return apiService.post('/auth/refresh', { refresh_token: refreshToken });
  }

  /**
   * Solicita restablecimiento de contraseña
   * @param {string} email - Correo electrónico
   * @returns {Promise} Promesa de confirmación
   */
  requestPasswordReset(email) {
    return apiService.post('/auth/password-reset-request', { email });
  }

  /**
   * Restablece la contraseña
   * @param {Object} data - Datos {token, email, new_password}
   * @returns {Promise} Promesa de confirmación
   */
  resetPassword(data) {
    return apiService.post('/auth/password-reset', {
      token: data.token,
      email: data.email,
      new_password: data.newPassword
    });
  }

  /**
   * Cambia la contraseña del usuario actual
   * @param {Object} data - Datos {current_password, new_password}
   * @returns {Promise} Promesa de confirmación
   */
  changePassword(data) {
    return apiService.post('/auth/change-password', {
      current_password: data.currentPassword,
      new_password: data.newPassword
    });
  }
}

export default new AuthService(); 