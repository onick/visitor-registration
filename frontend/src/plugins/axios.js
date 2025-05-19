import axios from 'axios';
import store from '@/store';
import router from '@/router';

// URL base para todas las peticiones
axios.defaults.baseURL = process.env.VUE_APP_API_URL || 'http://127.0.0.1:8080/api/v1';

// Configuración por defecto
axios.defaults.headers.common['Content-Type'] = 'application/json';
axios.defaults.headers.common['Accept'] = 'application/json';

// Interceptor para añadir el token a las peticiones
axios.interceptors.request.use(
  config => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
      console.log('Token añadido a la petición:', token.substring(0, 20) + '...');
      console.log('URL de la petición:', config.url);
      console.log('Método:', config.method.toUpperCase());
    } else {
      console.warn('No hay token disponible para la petición:', config.url);
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// Interceptor para manejar respuestas y errores
axios.interceptors.response.use(
  response => {
    console.log('Respuesta exitosa:', response.config.url, response.status);
    return response;
  },
  async error => {
    const originalRequest = error.config;
    
    console.error('Error en la petición:', originalRequest.url);
    if (error.response) {
      console.error('Código de estado:', error.response.status);
      console.error('Detalle del error:', error.response.data);
    }
    
    // Si el error es 401 (Unauthorized) y no es un intento de refresh token
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      // Marcar la petición como un intento de retry para evitar bucles infinitos
      originalRequest._retry = true;
      
      try {
        console.log('Intentando refrescar el token...');
        // Intentar refrescar el token
        await store.dispatch('auth/refreshToken');
        
        // Actualizar el token en la petición original
        const token = localStorage.getItem('access_token');
        if (token) {
          originalRequest.headers['Authorization'] = `Bearer ${token}`;
          console.log('Token refrescado y actualizado en la petición');
        } else {
          console.warn('No se pudo obtener un nuevo token');
        }
        
        // Reintentar la petición original con el nuevo token
        return axios(originalRequest);
      } catch (refreshError) {
        console.error('Error al refrescar el token:', refreshError);
        // Si falla el refresh token, redirigir al login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        
        // Mostrar notificación de sesión expirada
        store.dispatch('showNotification', {
          message: 'Tu sesión ha expirado. Por favor, inicia sesión nuevamente.',
          type: 'warning'
        });
        
        // Redirigir al login si no estamos ya en la página de login
        if (router.currentRoute.value.name !== 'login') {
          router.push({ name: 'login' });
        }
        
        return Promise.reject(refreshError);
      }
    }
    
    // Mostrar notificación de error si hay un mensaje en la respuesta
    if (error.response && error.response.data && error.response.data.message) {
      store.dispatch('showNotification', {
        message: error.response.data.message,
        type: 'error'
      });
    } else if (error.message) {
      store.dispatch('showNotification', {
        message: `Error: ${error.message}`,
        type: 'error'
      });
    }
    
    return Promise.reject(error);
  }
);

export default axios; 