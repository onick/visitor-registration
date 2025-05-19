import axios from 'axios';

// Función para transformar snake_case a camelCase
const transformUserData = (user) => {
  if (!user) return null;
  
  // Crear una copia del usuario para no modificar el original
  const transformedUser = { ...user };
  
  // Transformar first_name a firstName y last_name a lastName
  if ('first_name' in transformedUser) {
    transformedUser.firstName = transformedUser.first_name;
    delete transformedUser.first_name;
  }
  
  if ('last_name' in transformedUser) {
    transformedUser.lastName = transformedUser.last_name;
    delete transformedUser.last_name;
  }
  
  return transformedUser;
};

// Obtener y transformar usuario del localStorage
const getStoredUser = () => {
  const storedUser = localStorage.getItem('user');
  if (!storedUser) return null;
  
  try {
    const parsedUser = JSON.parse(storedUser);
    return transformUserData(parsedUser);
  } catch (e) {
    console.error('Error al parsear usuario del localStorage:', e);
    return null;
  }
};

// Estado inicial
const state = {
  token: localStorage.getItem('access_token') || null,
  refreshToken: localStorage.getItem('refresh_token') || null,
  user: getStoredUser(),
  loading: false,
  error: null
};

// Getters
const getters = {
  isAuthenticated: state => !!state.token,
  currentUser: state => state.user,
  userRole: state => state.user ? state.user.role : null,
  isAdmin: state => state.user && state.user.role === 'admin',
  isStaff: state => state.user && (state.user.role === 'staff' || state.user.role === 'admin'),
  isLoading: state => state.loading,
  error: state => state.error,
  getToken: state => state.token
};

// Acciones
const actions = {
  // Verificar el estado de autenticación
  async checkAuthStatus({ commit, dispatch, state }) {
    if (!state.token) {
      return null;
    }
    
    // Configurar token en axios
    axios.defaults.headers.common['Authorization'] = `Bearer ${state.token}`;
    
    try {
      // Intentar obtener el perfil del usuario para validar el token
      return await dispatch('getCurrentUser');
    } catch (error) {
      console.error('Error al verificar estado de autenticación:', error);
      
      // Si hay error de autenticación, intentar refrescar el token
      if (error.response && error.response.status === 401) {
        try {
          await dispatch('refreshToken');
          return await dispatch('getCurrentUser');
        } catch (refreshError) {
          // Si no se puede refrescar, limpiar sesión
          dispatch('logout');
          return null;
        }
      }
      
      throw error;
    }
  },
  
  // Iniciar sesión
  async login({ commit, dispatch }, credentials) {
    commit('SET_LOADING', true);
    commit('CLEAR_ERROR');
    
    try {
      // Modificar credenciales para usar username en lugar de email
      const loginData = {
        username: credentials.email, // Usar el email como username
        password: credentials.password
      };
      
      const response = await axios.post('/auth/login', loginData);
      
      const { access_token, refresh_token, user } = response.data;
      
      // Transformar los datos del usuario
      const transformedUser = transformUserData(user);
      
      // Guardar tokens y usuario en localStorage
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      localStorage.setItem('user', JSON.stringify(transformedUser));
      
      // Configurar token en axios para futuras peticiones
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      commit('SET_AUTH', { token: access_token, refreshToken: refresh_token, user: transformedUser });
      return transformedUser;
    } catch (error) {
      const errorMsg = error.response?.data?.message || error.response?.data?.error || 'Error al iniciar sesión';
      commit('SET_ERROR', errorMsg);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  // Iniciar sesión automáticamente como administrador
  async autoLogin({ commit }) {
    commit('SET_LOADING', true);
    commit('CLEAR_ERROR');
    
    try {
      // Usar credenciales del administrador
      const loginData = {
        username: 'admin', // Cambiado de admin@ccb.do a admin
        password: 'Admin123!'
      };
      
      const response = await axios.post('/auth/login', loginData);
      
      const { access_token, refresh_token, user } = response.data;
      
      // Transformar los datos del usuario
      const transformedUser = transformUserData(user);
      
      // Guardar tokens y usuario en localStorage
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      localStorage.setItem('user', JSON.stringify(transformedUser));
      
      // Configurar token en axios para futuras peticiones
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      commit('SET_AUTH', { token: access_token, refreshToken: refresh_token, user: transformedUser });
      return transformedUser;
    } catch (error) {
      const errorMsg = error.response?.data?.message || error.response?.data?.error || 'Error al iniciar sesión automática';
      commit('SET_ERROR', errorMsg);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  // Cerrar sesión
  async logout({ commit }) {
    try {
      // Intentar hacer logout en el servidor
      await axios.post('/auth/logout');
    } catch (error) {
      console.error('Error al cerrar sesión en el servidor:', error);
    } finally {
      // Limpiar localStorage y estado aunque falle el logout en el servidor
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      
      // Limpiar la cabecera de autorización
      delete axios.defaults.headers.common['Authorization'];
      
      commit('CLEAR_AUTH');
    }
  },
  
  // Refrescar token
  async refreshToken({ commit, state }) {
    if (!state.refreshToken) {
      throw new Error('No hay refresh token disponible');
    }
    
    commit('SET_LOADING', true);
    
    try {
      const response = await axios.post('/auth/refresh', {
        refresh_token: state.refreshToken
      });
      
      const { access_token, refresh_token } = response.data;
      
      // Actualizar localStorage
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      
      // Actualizar token en axios
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      commit('UPDATE_TOKENS', { token: access_token, refreshToken: refresh_token });
      return access_token;
    } catch (error) {
      commit('SET_ERROR', 'Error al refrescar el token');
      commit('CLEAR_AUTH');
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  // Registrar un nuevo usuario
  async register({ commit }, userData) {
    commit('SET_LOADING', true);
    commit('CLEAR_ERROR');
    
    try {
      const response = await axios.post('/auth/register', userData);
      return response.data;
    } catch (error) {
      const errorMsg = error.response?.data?.message || 'Error al registrar usuario';
      commit('SET_ERROR', errorMsg);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  // Obtener información del usuario actual
  async getCurrentUser({ commit, state }) {
    if (!state.token) {
      return null;
    }
    
    commit('SET_LOADING', true);
    
    try {
      const response = await axios.get('/auth/profile');
      const user = response.data;
      
      // Transformar los datos del usuario
      const transformedUser = transformUserData(user);
      
      // Actualizar localStorage
      localStorage.setItem('user', JSON.stringify(transformedUser));
      
      commit('SET_USER', transformedUser);
      return transformedUser;
    } catch (error) {
      console.error('Error al obtener perfil de usuario:', error);
      return null;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  // Actualizar perfil de usuario
  async updateProfile({ commit }, userData) {
    commit('SET_LOADING', true);
    
    try {
      const response = await axios.put('/auth/profile', userData);
      const updatedUser = response.data;
      
      // Transformar los datos del usuario
      const transformedUser = transformUserData(updatedUser);
      
      // Actualizar localStorage
      localStorage.setItem('user', JSON.stringify(transformedUser));
      
      commit('SET_USER', transformedUser);
      return transformedUser;
    } catch (error) {
      const errorMsg = error.response?.data?.message || 'Error al actualizar perfil';
      commit('SET_ERROR', errorMsg);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  // Cambiar contraseña
  async changePassword({ commit }, passwordData) {
    commit('SET_LOADING', true);
    commit('CLEAR_ERROR');
    
    try {
      const response = await axios.post('/auth/change-password', passwordData);
      return response.data;
    } catch (error) {
      const errorMsg = error.response?.data?.message || 'Error al cambiar contraseña';
      commit('SET_ERROR', errorMsg);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  // Solicitar reseteo de contraseña
  async requestPasswordReset({ commit }, email) {
    commit('SET_LOADING', true);
    commit('CLEAR_ERROR');
    
    try {
      const response = await axios.post('/auth/password-reset-request', { email });
      return response.data;
    } catch (error) {
      const errorMsg = error.response?.data?.message || error.response?.data?.error || 'Error al solicitar reseteo de contraseña';
      commit('SET_ERROR', errorMsg);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  // Resetear contraseña con token
  async resetPassword({ commit }, resetData) {
    commit('SET_LOADING', true);
    commit('CLEAR_ERROR');
    
    try {
      const response = await axios.post('/auth/password-reset', {
        token: resetData.token,
        email: resetData.email || '',
        new_password: resetData.password
      });
      return response.data;
    } catch (error) {
      const errorMsg = error.response?.data?.message || error.response?.data?.error || 'Error al resetear contraseña';
      commit('SET_ERROR', errorMsg);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  // Validar token
  async validateToken({ commit }, token) {
    try {
      // Como no hay un endpoint específico para validar token, simplemente verificamos
      // si el token existe y no está vacío
      return !!token;
    } catch (error) {
      return false;
    }
  },
  
  // Limpiar errores
  clearError({ commit }) {
    commit('CLEAR_ERROR');
  }
};

// Mutaciones
const mutations = {
  SET_AUTH(state, { token, refreshToken, user }) {
    state.token = token;
    state.refreshToken = refreshToken;
    state.user = user;
    state.error = null;
  },
  UPDATE_TOKENS(state, { token, refreshToken }) {
    state.token = token;
    state.refreshToken = refreshToken;
  },
  SET_USER(state, user) {
    state.user = user;
  },
  CLEAR_AUTH(state) {
    state.token = null;
    state.refreshToken = null;
    state.user = null;
  },
  SET_LOADING(state, status) {
    state.loading = status;
  },
  SET_ERROR(state, error) {
    state.error = error;
  },
  CLEAR_ERROR(state) {
    state.error = null;
  }
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};