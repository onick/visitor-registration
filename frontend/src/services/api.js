/**
 * Servicios para la comunicación con la API
 */
import axios from 'axios';

// Crear instancia de axios con la URL base
const apiClient = axios.create({
  baseURL: process.env.VUE_APP_API_URL || 'http://localhost:5000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000 // 10 segundos
});

// Servicios para eventos
export const eventService = {
  getEvents(params = {}) {
    return apiClient.get('/events', { params });
  },
  
  getEvent(id) {
    return apiClient.get(`/events/${id}`);
  },
  
  createEvent(eventData) {
    return apiClient.post('/events', eventData);
  },
  
  updateEvent(id, eventData) {
    return apiClient.put(`/events/${id}`, eventData);
  },
  
  deleteEvent(id) {
    return apiClient.delete(`/events/${id}`);
  }
};

// Servicios para visitantes
export const visitorService = {
  createVisitor(visitorData) {
    return apiClient.post('/visitors', visitorData);
  },
  
  checkIn(checkInData) {
    return apiClient.post('/visitors/check-in', checkInData);
  },
  
  getEventVisitors(eventId) {
    return apiClient.get(`/visitors/event/${eventId}`);
  }
};

// Servicios para kioscos
export const kioskService = {
  getKioskEvents(kioskId) {
    return apiClient.get(`/kiosks/${kioskId}/events`);
  },
  
  getKioskConfig(kioskId) {
    return apiClient.get(`/kiosks/${kioskId}/config`);
  },
  
  sendHeartbeat(kioskId) {
    return apiClient.post(`/kiosks/${kioskId}/heartbeat`);
  }
};

// Interceptor para manejar errores
apiClient.interceptors.response.use(
  response => response,
  error => {
    // Aquí se pueden manejar errores globales de la API
    console.error('Error en la solicitud API:', error);
    return Promise.reject(error);
  }
);

export default {
  eventService,
  visitorService,
  kioskService
};
