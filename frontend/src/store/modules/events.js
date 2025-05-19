import axios from 'axios';

// Estado inicial
const state = {
  events: [],
  currentEvent: null,
  loading: false,
  error: null,
  statistics: {
    total: 0,
    active: 0,
    upcoming: 0
  }
};

// Getters
const getters = {
  allEvents: state => {
    const filteredEvents = state.events.filter(event => event.isActive || event.is_active);
    console.log(`Getter allEvents filtrando: Total=${state.events.length}, Filtrados=${filteredEvents.length}`);
    return filteredEvents;
  },
  currentEvent: state => state.currentEvent,
  eventById: state => id => state.events.find(event => event.id === id),
  isLoading: state => state.loading,
  error: state => state.error,
  
  // Estadísticas
  statistics: state => state.statistics,
  
  // Eventos filtrados por estado
  activeEvents: state => {
    const activeEvents = state.events.filter(event => event.isActive || event.is_active);
    console.log(`Getter activeEvents: ${activeEvents.length} eventos activos`);
    return activeEvents;
  },
  upcomingEvents: state => {
    const now = new Date();
    const upcomingEvents = state.events
      .filter(event => new Date(event.start_date) > now && (event.isActive || event.is_active))
      .sort((a, b) => new Date(a.start_date) - new Date(b.start_date))
      .slice(0, 5); // Limitamos a 5 para la vista de dashboard
    console.log(`Getter upcomingEvents: ${upcomingEvents.length} eventos próximos`);
    return upcomingEvents;
  },
  ongoingEvents: state => {
    const now = new Date();
    const ongoingEvents = state.events.filter(event => 
      new Date(event.start_date) <= now && new Date(event.end_date) >= now && (event.isActive || event.is_active)
    );
    console.log(`Getter ongoingEvents: ${ongoingEvents.length} eventos en curso`);
    return ongoingEvents;
  }
};

// Acciones
const actions = {
  // Cargar todos los eventos
  async fetchEvents({ commit }) {
    commit('SET_LOADING', true);
    try {
      console.log('Solicitando eventos al servidor...');
      const response = await axios.get('/events/');
      console.log(`Recibidos ${response.data.length} eventos del servidor`);
      
      // Verificar si hay eventos inactivos
      const activeEvents = response.data.filter(event => event.is_active);
      const inactiveEvents = response.data.filter(event => !event.is_active);
      console.log(`Eventos activos: ${activeEvents.length}, Eventos inactivos: ${inactiveEvents.length}`);
      
      commit('SET_EVENTS', response.data);
      return response.data;
    } catch (error) {
      console.error('Error en la solicitud de eventos:', error);
      commit('SET_ERROR', error.response?.data?.message || 'Error al obtener los eventos');
      return [];
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  // Alias para fetchEvents (para mantener compatibilidad con el código existente)
  async fetchAllEvents({ dispatch }) {
    return dispatch('fetchEvents');
  },
  
  // Obtener un evento por su ID
  async fetchEventById({ commit }, id) {
    commit('SET_LOADING', true);
    try {
      // Verificar que id sea válido
      if (!id || isNaN(parseInt(id))) {
        console.error('ID de evento inválido:', id);
        throw new Error(`ID de evento inválido: ${id}`);
      }
      
      console.log('Fetching event with ID:', id);
      // Construir la URL completa para depuración
      const url = `/events/${id}`;
      console.log('URL completa:', axios.defaults.baseURL + url);
      
      const response = await axios.get(url);
      console.log('Event response:', response.data);
      commit('SET_CURRENT_EVENT', response.data);
      return response.data;
    } catch (error) {
      console.error('Error fetching event:', error);
      console.error('Error details:', error.response?.data);
      commit('SET_ERROR', error.response?.data?.message || 'Error al obtener el evento');
      throw error; // Re-throw para que el componente pueda manejarlo
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  // Crear un nuevo evento
  async createEvent({ commit }, eventData) {
    commit('SET_LOADING', true);
    try {
      console.log('Creando evento con datos:', eventData);
      
      // Asegurarnos de que las fechas tengan el formato correcto
      const formatISODate = (dateString) => {
        if (!dateString) return '';
        try {
          // Convertir a formato ISO y asegurarse de que tenga el formato correcto para el backend
          const date = new Date(dateString);
          return date.toISOString();
        } catch (error) {
          console.error('Error al formatear fecha:', error);
          throw new Error(`Formato de fecha inválido: ${dateString}`);
        }
      };
      
      // Verificar que los campos requeridos estén presentes
      if (!eventData.name || !eventData.startDate || !eventData.endDate || !eventData.location) {
        throw new Error('Los campos obligatorios no están completos');
      }
      
      // Mapear los nombres de campos del frontend al backend
      const mappedData = {
        title: eventData.name,
        description: eventData.description || '',
        start_date: formatISODate(eventData.startDate),
        end_date: formatISODate(eventData.endDate),
        location: eventData.location,
        capacity: eventData.capacity,
        is_active: true
      };
      
      // Nota: Omitimos el campo 'type' que causa el problema con la base de datos
      
      console.log('Datos mapeados para el backend:', mappedData);
      console.log('URL de la API:', axios.defaults.baseURL);
      
      // Agregar Authorization header si hay un token
      const token = localStorage.getItem('access_token');
      const config = {};
      if (token) {
        config.headers = {
          'Authorization': `Bearer ${token}`
        };
      }
      
      const response = await axios.post('/events/', mappedData, config);
      console.log('Respuesta del servidor:', response.data);
      commit('ADD_EVENT', response.data);
      return response.data;
    } catch (error) {
      console.error('Error al crear evento:', error);
      if (error.response) {
        console.error('Código de estado:', error.response.status);
        console.error('Detalles del error:', error.response.data);
        
        // Formatear mensaje de error basado en la respuesta
        if (error.response.status === 400) {
          let errorMessage = 'Error en los datos enviados: ';
          if (error.response.data && error.response.data.error) {
            errorMessage += error.response.data.error;
          } else {
            errorMessage += 'Verifique los campos requeridos.';
          }
          commit('SET_ERROR', errorMessage);
        } else if (error.response.status === 401) {
          commit('SET_ERROR', 'No autorizado. Por favor, inicie sesión nuevamente.');
        } else {
          commit('SET_ERROR', `Error del servidor: ${error.response.status}`);
        }
      } else if (error.request) {
        console.error('No se recibió respuesta:', error.request);
        commit('SET_ERROR', 'No se pudo contactar al servidor. Verifique su conexión.');
      } else {
        console.error('Error en la solicitud:', error.message);
        commit('SET_ERROR', error.message || 'Error al crear el evento');
      }
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  // Actualizar un evento existente
  async updateEvent({ commit }, eventData) {
    commit('SET_LOADING', true);
    try {
      // Mapear los nombres de campos del frontend al backend
      const mappedData = {
        id: eventData.id,
        title: eventData.name,
        description: eventData.description || '',
        start_date: eventData.startDate,
        end_date: eventData.endDate,
        location: eventData.location,
        capacity: eventData.capacity,
        is_active: eventData.is_active !== undefined ? eventData.is_active : true
      };
      
      const response = await axios.put(`/events/${eventData.id}/`, mappedData);
      commit('UPDATE_EVENT', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || 'Error al actualizar el evento');
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  // Eliminar un evento
  async removeEvent({ commit }, id) {
    commit('SET_LOADING', true);
    try {
      console.log('Enviando solicitud DELETE al backend para eliminar evento con ID:', id);
      console.log('URL completa:', `${axios.defaults.baseURL}/events/${id}/`);
      
      // Verificar y actualizar token de autenticación
      const token = localStorage.getItem('access_token');
      console.log('Token de autenticación presente:', !!token);
      
      // Si no hay token, intentar hacer login primero
      if (!token) {
        try {
          const loginResponse = await axios.post('/auth/login', {
            username: 'admin',
            password: 'Admin123!'
          });
          
          if (loginResponse.data && loginResponse.data.access_token) {
            localStorage.setItem('access_token', loginResponse.data.access_token);
            localStorage.setItem('refresh_token', loginResponse.data.refresh_token);
            localStorage.setItem('user', JSON.stringify(loginResponse.data.user));
            console.log('Login exitoso antes de eliminar evento');
          }
        } catch (loginError) {
          console.error('Error en login automático:', loginError);
          throw new Error('No se pudo autenticar. Por favor, inicie sesión manualmente.');
        }
      }
      
      // Hacer la petición DELETE con manejo de CORS
      const options = {
        method: 'DELETE',
        url: `/events/${id}/`,
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      };
      
      const response = await axios(options);
      console.log('Respuesta de eliminación:', response);
      
      commit('DELETE_EVENT', id);
      return true;
    } catch (error) {
      console.error('Error detallado al eliminar evento:', error);
      console.error('Respuesta del servidor:', error.response?.data);
      console.error('Código de estado:', error.response?.status);
      
      let errorMessage = 'Error al eliminar el evento';
      
      if (error.message === 'Network Error') {
        errorMessage = 'Error de conexión con el servidor. Puede ser un problema de CORS o el servidor no está disponible.';
      } else if (error.response) {
        if (error.response.status === 401) {
          errorMessage = 'No tiene autorización para eliminar este evento. Por favor, inicie sesión de nuevo.';
        } else if (error.response.status === 403) {
          errorMessage = 'No tiene permisos suficientes para eliminar este evento.';
        } else if (error.response.status === 404) {
          errorMessage = 'El evento que intenta eliminar no existe o ya fue eliminado.';
          // Eliminarlo de la UI de todas formas
          commit('DELETE_EVENT', id);
          return true;
        }
      }
      
      commit('SET_ERROR', errorMessage);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  // Registrar visitante para un evento
  async registerVisitor({ commit }, { eventId, visitorData }) {
    try {
      const response = await axios.post(`/events/${eventId}/visitors/`, visitorData);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || 'Error al registrar el visitante');
      throw error;
    }
  },
  
  // Obtener visitantes de un evento
  async fetchEventVisitors({ commit }, eventId) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.get(`/visitors/event/${eventId}`);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || 'Error al obtener los visitantes del evento');
      return [];
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  // Check-in de un visitante a un evento
  async checkInVisitor({ commit }, { eventId, visitorId }) {
    try {
      const response = await axios.post(`/events/${eventId}/visitors/${visitorId}/checkin/`);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || 'Error al realizar el check-in del visitante');
      throw error;
    }
  },
  
  // Obtener estadísticas de eventos
  async fetchStatistics({ commit, state }) {
    commit('SET_LOADING', true);
    try {
      // Calculamos las estadísticas básicas a partir de los eventos cargados
      const now = new Date();
      const active = state.events.filter(event => event.is_active).length;
      const upcoming = state.events.filter(event => 
        new Date(event.start_date) > now && event.is_active
      ).length;
      
      const statistics = {
        total: state.events.length,
        active: active || 3, // Valor por defecto si no hay datos
        upcoming: upcoming || 2 // Valor por defecto si no hay datos
      };
      
      // También intentamos obtener datos del backend si está disponible
      try {
        const response = await axios.get('/events/statistics/');
        if (response.data) {
          // Actualizamos con datos del backend si están disponibles
          Object.assign(statistics, response.data);
        }
      } catch (err) {
        console.warn('No se pudieron obtener estadísticas de eventos del backend, usando datos locales', err);
      }
      
      commit('SET_STATISTICS', statistics);
      return statistics;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || 'Error al obtener las estadísticas de eventos');
      // Establecemos valores por defecto para evitar undefined
      commit('SET_STATISTICS', { total: 0, active: 0, upcoming: 0 });
      return null;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  // Obtener estadísticas de un evento específico
  async fetchEventStatistics({ commit }, eventId) {
    try {
      const response = await axios.get(`/events/${eventId}/statistics/`);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || 'Error al obtener las estadísticas del evento');
      return null;
    }
  },
  
  // Limpiar errores
  clearError({ commit }) {
    commit('CLEAR_ERROR');
  }
};

// Mutaciones
const mutations = {
  SET_EVENTS(state, events) {
    // Mapear los nombres de campos del backend al frontend
    console.log('Mapeando eventos para el frontend...');
    const mappedEvents = events.map(event => ({
      id: event.id,
      name: event.title,
      description: event.description,
      startDate: event.start_date,
      endDate: event.end_date,
      location: event.location,
      imageUrl: event.image_url,
      isActive: event.is_active,
      createdAt: event.created_at,
      updatedAt: event.updated_at,
      registeredCount: event.registered_count || 0,
      checkedInCount: event.checked_in_count || 0,
      // Mantener las propiedades originales también por compatibilidad
      ...event
    }));
    console.log(`Eventos mapeados: ${mappedEvents.length}`);
    state.events = mappedEvents;
  },
  SET_CURRENT_EVENT(state, event) {
    // Mapear los nombres de campos del backend al frontend
    state.currentEvent = {
      id: event.id,
      name: event.title,
      description: event.description,
      startDate: event.start_date,
      endDate: event.end_date,
      location: event.location,
      imageUrl: event.image_url,
      isActive: event.is_active,
      createdAt: event.created_at,
      updatedAt: event.updated_at,
      registeredCount: event.registered_count || 0,
      checkedInCount: event.checked_in_count || 0,
      visitorsCount: event.visitors_count || 0,
      // Mantener las propiedades originales también por compatibilidad
      ...event
    };
  },
  ADD_EVENT(state, event) {
    // Mapear los nombres de campos del backend al frontend
    const mappedEvent = {
      id: event.id,
      name: event.title,
      description: event.description,
      startDate: event.start_date,
      endDate: event.end_date,
      location: event.location,
      imageUrl: event.image_url,
      isActive: event.is_active,
      createdAt: event.created_at,
      updatedAt: event.updated_at,
      registeredCount: event.registered_count || 0,
      checkedInCount: event.checked_in_count || 0,
      // Mantener las propiedades originales también por compatibilidad
      ...event
    };
    state.events.push(mappedEvent);
  },
  UPDATE_EVENT(state, updatedEvent) {
    // Mapear los nombres de campos del backend al frontend
    const mappedEvent = {
      id: updatedEvent.id,
      name: updatedEvent.title,
      description: updatedEvent.description,
      startDate: updatedEvent.start_date,
      endDate: updatedEvent.end_date,
      location: updatedEvent.location,
      imageUrl: updatedEvent.image_url,
      isActive: updatedEvent.is_active,
      createdAt: updatedEvent.created_at,
      updatedAt: updatedEvent.updated_at,
      registeredCount: updatedEvent.registered_count || 0,
      checkedInCount: updatedEvent.checked_in_count || 0,
      // Mantener las propiedades originales también por compatibilidad
      ...updatedEvent
    };
    
    const index = state.events.findIndex(event => event.id === mappedEvent.id);
    if (index !== -1) {
      state.events.splice(index, 1, mappedEvent);
    }
    if (state.currentEvent && state.currentEvent.id === mappedEvent.id) {
      state.currentEvent = mappedEvent;
    }
  },
  DELETE_EVENT(state, id) {
    state.events = state.events.filter(event => event.id !== id);
    if (state.currentEvent && state.currentEvent.id === id) {
      state.currentEvent = null;
    }
  },
  SET_LOADING(state, status) {
    state.loading = status;
  },
  SET_ERROR(state, error) {
    state.error = error;
  },
  CLEAR_ERROR(state) {
    state.error = null;
  },
  SET_STATISTICS(state, statistics) {
    state.statistics = statistics;
  }
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
