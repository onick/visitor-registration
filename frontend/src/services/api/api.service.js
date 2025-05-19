import axios from 'axios';
import store from '@/store';

/**
 * Servicio base para todas las llamadas a API
 */
class ApiService {
  /**
   * Constructor del servicio
   */
  constructor() {
    this.axios = axios;
    this.axios.defaults.baseURL = process.env.VUE_APP_API_URL || '/api/v1';
  }

  /**
   * Establece el token de autenticación para las peticiones
   * @param {string} token - Token JWT
   */
  setAuthHeader(token) {
    this.axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }

  /**
   * Elimina el token de autenticación
   */
  removeAuthHeader() {
    delete this.axios.defaults.headers.common['Authorization'];
  }

  /**
   * Realiza una petición GET
   * @param {string} resource - Ruta del recurso
   * @param {Object} params - Parámetros de la petición
   * @returns {Promise} Promesa con la respuesta
   */
  get(resource, params = {}) {
    return this.axios.get(resource, { params });
  }

  /**
   * Realiza una petición POST
   * @param {string} resource - Ruta del recurso
   * @param {Object} data - Datos a enviar
   * @returns {Promise} Promesa con la respuesta
   */
  post(resource, data) {
    return this.axios.post(resource, data);
  }

  /**
   * Realiza una petición PUT
   * @param {string} resource - Ruta del recurso
   * @param {Object} data - Datos a enviar
   * @returns {Promise} Promesa con la respuesta
   */
  put(resource, data) {
    return this.axios.put(resource, data);
  }

  /**
   * Realiza una petición DELETE
   * @param {string} resource - Ruta del recurso
   * @param {Object} data - Datos a enviar
   * @returns {Promise} Promesa con la respuesta
   */
  delete(resource, data = {}) {
    return this.axios.delete(resource, { data });
  }

  /**
   * Realiza una petición PATCH
   * @param {string} resource - Ruta del recurso
   * @param {Object} data - Datos a enviar
   * @returns {Promise} Promesa con la respuesta
   */
  patch(resource, data) {
    return this.axios.patch(resource, data);
  }
}

// Crear instancia del servicio
const apiService = new ApiService();

// Interceptor para manejar errores
apiService.axios.interceptors.response.use(
  (response) => response,
  (error) => {
    const { status } = error.response || {};
    
    if (status === 401) {
      // Redirigir a login si el token expiró
      store.dispatch('auth/logout');
      window.location.href = '/login';
    }
    
    return Promise.reject(error);
  }
);

export default apiService; 