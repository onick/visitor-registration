import { createStore } from 'vuex';
import auth from './modules/auth';
import events from './modules/events';
import visitors from './modules/visitors';
import kiosks from './modules/kiosks';
import users from './modules/users';

export default createStore({
  state: {
    appName: 'Centro Cultural Banreservas',
    loading: false,
    notification: {
      show: false,
      message: '',
      type: 'info'
    }
  },
  mutations: {
    SET_LOADING(state, value) {
      state.loading = value;
    },
    SET_NOTIFICATION(state, { message, type = 'info' }) {
      state.notification = {
        show: true,
        message,
        type
      };
    },
    CLEAR_NOTIFICATION(state) {
      state.notification = {
        show: false,
        message: '',
        type: 'info'
      };
    }
  },
  actions: {
    setLoading({ commit }, value) {
      commit('SET_LOADING', value);
    },
    showNotification({ commit }, notification) {
      commit('SET_NOTIFICATION', notification);
      setTimeout(() => {
        commit('CLEAR_NOTIFICATION');
      }, 5000);
    }
  },
  modules: {
    auth,
    events,
    visitors,
    kiosks,
    users
  }
}); 