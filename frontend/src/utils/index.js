/**
 * Utilidades generales para la aplicación
 */

// Formatear fecha para mostrar
export const formatDate = (dateString, locale = 'es-ES') => {
  if (!dateString) return '';
  
  const date = new Date(dateString);
  
  return date.toLocaleDateString(locale, {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};

// Formatear hora
export const formatTime = (dateString, locale = 'es-ES') => {
  if (!dateString) return '';
  
  const date = new Date(dateString);
  
  return date.toLocaleTimeString(locale, {
    hour: '2-digit',
    minute: '2-digit'
  });
};

// Comprobar si un evento está en curso actualmente
export const isEventActive = (startDate, endDate) => {
  const now = new Date();
  const start = new Date(startDate);
  const end = new Date(endDate);
  
  return start <= now && end >= now;
};

// Ordenar eventos por proximidad (primero los actuales, luego los próximos)
export const sortEventsByProximity = (events) => {
  const now = new Date();
  
  return [...events].sort((a, b) => {
    const aStart = new Date(a.start_date);
    const bStart = new Date(b.start_date);
    
    // Si a está en curso y b no, a va primero
    if (isEventActive(a.start_date, a.end_date) && !isEventActive(b.start_date, b.end_date)) {
      return -1;
    }
    
    // Si b está en curso y a no, b va primero
    if (!isEventActive(a.start_date, a.end_date) && isEventActive(b.start_date, b.end_date)) {
      return 1;
    }
    
    // Si ambos están en curso o ambos son futuros, ordenar por hora de inicio
    return aStart - bStart;
  });
};

// Validación básica de correo electrónico
export const isValidEmail = (email) => {
  const re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
  return re.test(String(email).toLowerCase());
};

// Validación básica de teléfono
export const isValidPhone = (phone) => {
  const re = /^[+]?[(]?[0-9]{3}[)]?[-\s.]?[0-9]{3}[-\s.]?[0-9]{4,6}$/;
  return re.test(String(phone));
};

// Detección de inactividad y reinicio de temporizador
export const setupIdleTimer = (timeout, callback) => {
  let idleTimer = null;
  
  const resetTimer = () => {
    clearTimeout(idleTimer);
    idleTimer = setTimeout(callback, timeout);
  };
  
  // Eventos que reinician el temporizador
  const events = ['mousemove', 'mousedown', 'keypress', 'touchstart', 'touchmove'];
  
  // Configurar listeners
  events.forEach(event => {
    document.addEventListener(event, resetTimer);
  });
  
  // Iniciar temporizador
  resetTimer();
  
  // Función para limpiar
  return () => {
    clearTimeout(idleTimer);
    events.forEach(event => {
      document.removeEventListener(event, resetTimer);
    });
  };
};

// Generar ID único
export const generateUniqueId = () => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
};

export default {
  formatDate,
  formatTime,
  isEventActive,
  sortEventsByProximity,
  isValidEmail,
  isValidPhone,
  setupIdleTimer,
  generateUniqueId
};
