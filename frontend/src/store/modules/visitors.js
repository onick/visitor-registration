import axios from 'axios';

// Estado inicial
const state = {
  visitors: [],
  currentVisitor: null,
  loading: false,
  error: null,
  pagination: {
    total: 0,
    page: 1,
    limit: 10
  },
  statistics: {
    total: 0,
    checkedIn: 0,
    today: 0
  }
};

// Getters
const getters = {
  allVisitors: state => state.visitors,
  currentVisitor: state => state.currentVisitor,
  visitorById: state => id => state.visitors.find(visitor => visitor.id === id),
  isLoading: state => state.loading,
  error: state => state.error,
  pagination: state => state.pagination,
  
  // Estadísticas
  statistics: state => state.statistics,
  
  // Estadísticas básicas
  visitorCount: state => state.visitors.length,
  checkedInCount: state => state.visitors.filter(visitor => visitor.checked_in).length,
  recentVisitors: state => [...state.visitors]
    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    .slice(0, 5)
};

// Acciones
const actions = {
  // Cargar todos los visitantes
  async fetchVisitors({ commit }, params = {}) {
    commit('SET_LOADING', true);
    console.log('Iniciando fetchVisitors con parámetros:', params);
    try {
      // Establecer un límite más alto por defecto para mostrar más visitantes
      if (!params.limit) params.limit = 100;
      
      const query = new URLSearchParams();
      
      // Agregar parámetros de paginación y filtrado
      if (params.page) query.append('page', params.page);
      if (params.limit) query.append('limit', params.limit);
      if (params.search) query.append('search', params.search);
      if (params.event_id) query.append('event_id', params.event_id);
      
      console.log('URL de la petición:', `/visitors?${query.toString()}`);
      console.log('URL base actual:', axios.defaults.baseURL);
      
      const response = await axios.get(`/visitors?${query.toString()}`);
      console.log('Respuesta fetchVisitors:', response.data);
      
      // Si la respuesta incluye paginación
      if (response.data && response.data.pagination) {
        commit('SET_PAGINATION', response.data.pagination);
        commit('SET_VISITORS', response.data.items);
      } else if (Array.isArray(response.data)) {
        // Si es un array simple de visitantes
        commit('SET_VISITORS', response.data);
      } else {
        console.error('Formato de respuesta inesperado:', response.data);
        commit('SET_VISITORS', []);
        commit('SET_ERROR', 'Formato de respuesta no reconocido');
      }
      
      return response.data;
    } catch (error) {
      console.error('Error en fetchVisitors:', error);
      console.error('Detalles del error:', error.response?.data);
      console.error('Código de estado:', error.response?.status);
      commit('SET_ERROR', error.response?.data?.message || 'Error al obtener los visitantes');
      return [];
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  // Obtener un visitante por su ID
  async fetchVisitorById({ commit }, id) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.get(`/visitors/${id}`);
      commit('SET_CURRENT_VISITOR', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || 'Error al obtener el visitante');
      return null;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  // Crear un nuevo visitante
  async createVisitor({ commit }, visitorData) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.post('/visitors', visitorData);
      commit('ADD_VISITOR', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || 'Error al crear el visitante');
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  // Actualizar un visitante existente
  async updateVisitor({ commit }, visitorData) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.put(`/visitors/${visitorData.id}`, visitorData);
      commit('UPDATE_VISITOR', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || 'Error al actualizar el visitante');
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  // Eliminar un visitante
  async removeVisitor({ commit }, id) {
    commit('SET_LOADING', true);
    try {
      await axios.delete(`/visitors/${id}`);
      commit('DELETE_VISITOR', id);
      return true;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || 'Error al eliminar el visitante');
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  // Registrar visitante para un evento
  async registerVisitorForEvent({ commit }, { eventId, visitorData }) {
    commit('SET_LOADING', true);
    console.log('Registrando visitante para evento:', eventId);
    console.log('Datos del visitante:', visitorData);
    try {
      // Formatear los datos según lo que espera el backend
      const formattedData = {
        name: `${visitorData.first_name} ${visitorData.last_name}`,
        email: visitorData.email,
        phone: visitorData.phone,
        event_id: eventId,
        kiosk_id: process.env.VUE_APP_KIOSK_ID || 1
      };
      
      console.log('Datos formateados para el backend:', formattedData);
      
      // Usar el endpoint correcto para el registro de visitantes
      const response = await axios.post('/visitors/register', formattedData);
      console.log('Respuesta de registro:', response.data);
      
      // La respuesta ya incluye registration_code, success, y otros datos
      if (response.data && response.data.success) {
        // Crear un objeto visitante con los datos disponibles
        const visitor = {
          id: response.data.visitor_id,
          name: `${visitorData.first_name} ${visitorData.last_name}`,
          email: visitorData.email,
          phone: visitorData.phone,
          event_id: eventId,
          registration_code: response.data.registration_code
        };
        commit('ADD_VISITOR', visitor);
      }
      
      return response.data;
    } catch (error) {
      console.error('Error al registrar visitante:', error);
      console.error('Detalles del error:', error.response?.data);
      console.error('Código de estado:', error.response?.status);
      commit('SET_ERROR', error.response?.data?.message || 'Error al registrar el visitante para el evento');
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  // Check-in de un visitante
  async checkInVisitor({ commit }, { eventId, visitorId }) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.post(`/events/${eventId}/visitors/${visitorId}/checkin`);
      commit('UPDATE_VISITOR_CHECKIN', { id: visitorId, checked_in: true });
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || 'Error al realizar el check-in del visitante');
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  // Obtener estadísticas de visitantes
  async fetchStatistics({ commit }) {
    commit('SET_LOADING', true);
    try {
      // En un entorno real, obtendríamos datos del backend
      // Por ahora, simulamos datos de estadísticas 
      const statisticsData = {
        total: state.visitors.length || 25,  // Fallback a un valor predeterminado
        checkedIn: state.visitors.filter(v => v.checked_in).length || 8,
        today: 5
      };
      
      // También intentamos obtener datos del backend si está disponible
      try {
        const response = await axios.get('/visitors/statistics');
        if (response.data) {
          statisticsData.total = response.data.total || statisticsData.total;
          statisticsData.checkedIn = response.data.checkedIn || statisticsData.checkedIn;
          statisticsData.today = response.data.today || statisticsData.today;
        }
      } catch (err) {
        console.warn('No se pudieron obtener estadísticas del backend, usando datos locales', err);
      }
      
      commit('SET_STATISTICS', statisticsData);
      return statisticsData;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || 'Error al obtener las estadísticas de visitantes');
      // Si hay un error, igualmente establecemos algunos datos por defecto para evitar undefined
      commit('SET_STATISTICS', { total: 0, checkedIn: 0, today: 0 });
      return null;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  // Obtener un visitante por su código de registro
  async getVisitorByCode({ commit }, code) {
    commit('SET_LOADING', true);
    console.log('Verificando código:', code);
    console.log('Tipo de código:', typeof code);
    console.log('Longitud:', code.length);
    
    try {
      const requestData = { code };
      console.log('Enviando datos:', JSON.stringify(requestData));
      
      const response = await axios.post('/visitors/verify-code', requestData);
      console.log('Respuesta de verificación:', response.data);
      
      if (response.data.visitor) {
        commit('SET_CURRENT_VISITOR', response.data.visitor);
      }
      
      return response.data;
    } catch (error) {
      console.error('Error al verificar código:', error);
      console.error('Detalles del error:', error.response?.data);
      console.error('Código de estado:', error.response?.status);
      console.error('Mensaje del servidor:', error.response?.data?.error);
      commit('SET_ERROR', error.response?.data?.error || error.response?.data?.message || 'Error al verificar el código');
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  // Limpiar errores
  clearError({ commit }) {
    commit('CLEAR_ERROR');
  }
};

// Mutaciones
const mutations = {
  SET_VISITORS(state, visitors) {
    state.visitors = visitors;
  },
  SET_CURRENT_VISITOR(state, visitor) {
    state.currentVisitor = visitor;
  },
  ADD_VISITOR(state, visitor) {
    state.visitors.push(visitor);
  },
  UPDATE_VISITOR(state, updatedVisitor) {
    const index = state.visitors.findIndex(visitor => visitor.id === updatedVisitor.id);
    if (index !== -1) {
      state.visitors.splice(index, 1, updatedVisitor);
    }
    if (state.currentVisitor && state.currentVisitor.id === updatedVisitor.id) {
      state.currentVisitor = updatedVisitor;
    }
  },
  UPDATE_VISITOR_CHECKIN(state, { id, checked_in }) {
    const index = state.visitors.findIndex(visitor => visitor.id === id);
    if (index !== -1) {
      state.visitors[index] = {
        ...state.visitors[index],
        checked_in: checked_in
      };
    }
    if (state.currentVisitor && state.currentVisitor.id === id) {
      state.currentVisitor = {
        ...state.currentVisitor,
        checked_in: checked_in
      };
    }
  },
  DELETE_VISITOR(state, id) {
    state.visitors = state.visitors.filter(visitor => visitor.id !== id);
    if (state.currentVisitor && state.currentVisitor.id === id) {
      state.currentVisitor = null;
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
  SET_PAGINATION(state, pagination) {
    state.pagination = pagination;
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