// Sistema de eventos para Vue 3 (reemplazo para $root.$on, $root.$emit, etc.)
import { ref } from 'vue';

// Singleton para el bus de eventos
class EventBus {
  constructor() {
    this.events = {};
  }

  // Equivalente a $on
  on(event, callback) {
    if (!this.events[event]) {
      this.events[event] = [];
    }
    this.events[event].push(callback);
  }

  // Equivalente a $off
  off(event, callback) {
    if (!this.events[event]) {
      return;
    }
    
    if (!callback) {
      // Si no se proporciona callback, eliminar todos los listeners del evento
      delete this.events[event];
      return;
    }
    
    // Filtrar el callback específico
    this.events[event] = this.events[event].filter(cb => cb !== callback);
  }

  // Equivalente a $emit
  emit(event, ...args) {
    if (!this.events[event]) {
      return;
    }
    this.events[event].forEach(callback => {
      callback(...args);
    });
  }
}

// Exportar una única instancia para usar en toda la aplicación
export default new EventBus();
