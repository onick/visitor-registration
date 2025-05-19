import axios from 'axios';

// Estado inicial
const state = {
  users: [],
  currentUser: null,
  loading: false,
  error: null,
  pagination: {
    total: 0,
    page: 1,
    limit: 10
  }
};

// Getters
const getters = {
  allUsers: state => state.users,
  currentUser: state => state.currentUser,
  userById: state => id => state.users.find(user => user.id === id),
  isLoading: state => state.loading,
  error: state => state.error,
  pagination: state => state.pagination,
  
  // Usuarios por rol
  adminUsers: state => state.users.filter(user => user.role === 'admin'),
  staffUsers: state => state.users.filter(user => user.role === 'staff'),
  
  // Usuarios activos/inactivos
  activeUsers: state => state.users.filter(user => user.is_active),
  inactiveUsers: state => state.users.filter(user => !user.is_active)
};

// Acciones
const actions = {
  // Cargar todos los usuarios
  async fetchUsers({ commit }, params = {}) {
    commit('SET_LOADING', true);
    try {
      const query = new URLSearchParams();
      
      // Agregar parámetros de paginación y filtrado
      if (params.page) query.append('page', params.page);
      if (params.limit) query.append('limit', params.limit);
      if (params.search) query.append('search', params.search);
      if (params.role) query.append('role', params.role);
      if (params.is_active !== undefined) query.append('is_active', params.is_active);
      
      const response = await axios.get(`/users?${query.toString()}`);
      
      // Si la respuesta incluye paginación
      if (response.data.pagination) {
        commit('SET_PAGINATION', response.data.pagination);
        commit('SET_USERS', response.data.items);
      } else {
        // Si es un array simple de usuarios
        commit('SET_USERS', response.data);
      }
      
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || 'Error al obtener los usuarios');
      return [];
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  // Obtener un usuario por su ID
  async fetchUserById({ commit }, id) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.get(`/users/${id}`);
      commit('SET_CURRENT_USER', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || 'Error al obtener el usuario');
      return null;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  // Crear un nuevo usuario
  async createUser({ commit }, userData) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.post('/users', userData);
      commit('ADD_USER', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || 'Error al crear el usuario');
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  // Actualizar un usuario existente
  async updateUser({ commit }, userData) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.put(`/users/${userData.id}`, userData);
      commit('UPDATE_USER', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || 'Error al actualizar el usuario');
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  // Eliminar un usuario
  async removeUser({ commit }, id) {
    commit('SET_LOADING', true);
    try {
      await axios.delete(`/users/${id}`);
      commit('DELETE_USER', id);
      return true;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || 'Error al eliminar el usuario');
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  // Activar/desactivar un usuario
  async toggleUserStatus({ commit }, { id, is_active }) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.patch(`/users/${id}/status`, { is_active });
      commit('UPDATE_USER', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || 'Error al cambiar el estado del usuario');
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  // Cambiar el rol de un usuario
  async changeUserRole({ commit }, { id, role }) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.patch(`/users/${id}/role`, { role });
      commit('UPDATE_USER', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || 'Error al cambiar el rol del usuario');
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  // Resetear la contraseña de un usuario (solo admin)
  async resetUserPassword({ commit }, { id, password }) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.post(`/users/${id}/reset-password`, { password });
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || 'Error al resetear la contraseña');
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
  SET_USERS(state, users) {
    state.users = users;
  },
  SET_CURRENT_USER(state, user) {
    state.currentUser = user;
  },
  ADD_USER(state, user) {
    state.users.push(user);
  },
  UPDATE_USER(state, updatedUser) {
    const index = state.users.findIndex(user => user.id === updatedUser.id);
    if (index !== -1) {
      state.users.splice(index, 1, updatedUser);
    }
    if (state.currentUser && state.currentUser.id === updatedUser.id) {
      state.currentUser = updatedUser;
    }
  },
  DELETE_USER(state, id) {
    state.users = state.users.filter(user => user.id !== id);
    if (state.currentUser && state.currentUser.id === id) {
      state.currentUser = null;
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
  }
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}; 