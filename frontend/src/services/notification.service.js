import eventBus from '@/utils/eventBus';

/**
 * Servicio para gestionar notificaciones en tiempo real
 */
class NotificationService {
  /**
   * Muestra una notificación
   * @param {Object} notification - Datos de la notificación
   * @param {string} notification.message - Mensaje a mostrar
   * @param {string} notification.type - Tipo de notificación (info, success, warning, error)
   * @param {number} notification.duration - Duración en ms (opcional)
   */
  showNotification(notification) {
    eventBus.emit('notification', notification);
  }

  /**
   * Muestra una notificación de éxito
   * @param {string} message - Mensaje a mostrar
   * @param {number} duration - Duración en ms (opcional)
   */
  success(message, duration) {
    this.showNotification({
      message,
      type: 'success',
      duration
    });
  }

  /**
   * Muestra una notificación de información
   * @param {string} message - Mensaje a mostrar
   * @param {number} duration - Duración en ms (opcional)
   */
  info(message, duration) {
    this.showNotification({
      message,
      type: 'info',
      duration
    });
  }

  /**
   * Muestra una notificación de advertencia
   * @param {string} message - Mensaje a mostrar
   * @param {number} duration - Duración en ms (opcional)
   */
  warning(message, duration) {
    this.showNotification({
      message,
      type: 'warning',
      duration
    });
  }

  /**
   * Muestra una notificación de error
   * @param {string} message - Mensaje a mostrar
   * @param {number} duration - Duración en ms (opcional)
   */
  error(message, duration) {
    this.showNotification({
      message,
      type: 'error',
      duration
    });
  }

  /**
   * Notifica sobre un nuevo registro de visitante
   * @param {Object} visitor - Datos del visitante
   * @param {Object} event - Datos del evento
   */
  notifyNewRegistration(visitor, event) {
    this.success(`Nuevo registro: ${visitor.name} para el evento ${event.name}`);
    
    // Emitir evento específico para que los componentes puedan reaccionar
    eventBus.emit('visitor-registered', { visitor, event });
  }

  /**
   * Notifica sobre un nuevo check-in de visitante
   * @param {Object} visitor - Datos del visitante
   * @param {Object} event - Datos del evento
   */
  notifyCheckIn(visitor, event) {
    this.info(`Check-in completado: ${visitor.name} para el evento ${event.name}`);
    
    // Emitir evento específico para que los componentes puedan reaccionar
    eventBus.emit('visitor-checked-in', { visitor, event });
  }
}

export default new NotificationService();