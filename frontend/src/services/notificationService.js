/**
 * Servicio de notificaciones para la aplicación
 * Utiliza vue-toastification con estilos personalizados CCB
 */

import { useToast } from 'vue-toastification';

let toastInstance = null;

// Obtener la instancia de toast
const getToast = () => {
  if (!toastInstance) {
    toastInstance = useToast();
  }
  return toastInstance;
};

const NotificationService = {
  /**
   * Muestra una notificación de éxito
   * @param {string} message - Mensaje a mostrar
   * @param {object} options - Opciones adicionales
   */
  success(message, options = {}) {
    const toast = getToast();
    toast.success(message, {
      timeout: 3000,
      ...options
    });
  },

  /**
   * Muestra una notificación de error
   * @param {string} message - Mensaje a mostrar
   * @param {object} options - Opciones adicionales
   */
  error(message, options = {}) {
    const toast = getToast();
    toast.error(message, {
      timeout: 5000,
      ...options
    });
  },

  /**
   * Muestra una notificación de advertencia
   * @param {string} message - Mensaje a mostrar
   * @param {object} options - Opciones adicionales
   */
  warning(message, options = {}) {
    const toast = getToast();
    toast.warning(message, {
      timeout: 4000,
      ...options
    });
  },

  /**
   * Muestra una notificación informativa
   * @param {string} message - Mensaje a mostrar
   * @param {object} options - Opciones adicionales
   */
  info(message, options = {}) {
    const toast = getToast();
    toast.info(message, {
      timeout: 3000,
      ...options
    });
  },

  /**
   * Muestra una notificación de carga
   * @param {string} message - Mensaje a mostrar
   * @returns {object} - Referencia del toast para actualizarlo
   */
  loading(message) {
    const toast = getToast();
    return toast.info(message, {
      timeout: false,
      closeButton: false,
      closeOnClick: false,
      icon: '⏳'
    });
  },

  /**
   * Actualiza un toast existente
   * @param {object} id - ID del toast a actualizar
   * @param {object} options - Nuevas opciones
   */
  update(id, options) {
    const toast = getToast();
    toast.update(id, options);
  },

  /**
   * Elimina un toast específico
   * @param {object} id - ID del toast a eliminar
   */
  dismiss(id) {
    const toast = getToast();
    toast.dismiss(id);
  },

  /**
   * Elimina todos los toasts
   */
  clear() {
    const toast = getToast();
    toast.clear();
  }
};

// Función de ayuda para manejar respuestas de API
const handleApiResponse = (response, successMessage) => {
  if (response.error) {
    NotificationService.error(response.error);
    return false;
  }
  if (successMessage) {
    NotificationService.success(successMessage);
  }
  return true;
};

// Función de ayuda para manejar errores de API
const handleApiError = (error) => {
  const message = error.response?.data?.error || 
                  error.message || 
                  'Ha ocurrido un error inesperado';
  NotificationService.error(message);
};

export { NotificationService, handleApiResponse, handleApiError };
export default NotificationService;
