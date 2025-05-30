<template>
  <nav class="navigation" :class="{ 'is-expanded': isExpanded }">
    <div class="nav-header">
      <div class="logo-container">
        <img src="@/assets/images/logo.png" alt="Centro Cultural Banreservas" class="logo-image">
      </div>
      <button class="toggle-button" @click="toggleNav">
        <span class="bar"></span>
        <span class="bar"></span>
        <span class="bar"></span>
      </button>
    </div>
    
    <div class="nav-links">
      <router-link to="/admin/dashboard" class="nav-link" v-if="isAdmin">
        <img src="@/assets/icons/chart-line.svg" alt="Dashboard" class="nav-icon" /> Dashboard
      </router-link>
      <router-link to="/admin/events" class="nav-link" v-if="isAdmin">
        <img src="@/assets/icons/calendar.svg" alt="Eventos" class="nav-icon" /> Eventos
      </router-link>
      <router-link to="/admin/visitors" class="nav-link" v-if="isAdmin">
        <img src="@/assets/icons/users.svg" alt="Visitantes" class="nav-icon" /> Visitantes
      </router-link>
      <router-link to="/admin/kiosks" class="nav-link" v-if="isAdmin">
        <img src="@/assets/icons/tablet.svg" alt="Kioscos" class="nav-icon" /> Kioscos
      </router-link>
      <router-link to="/admin/users" class="nav-link" v-if="isAdmin && hasUserManagementAccess">
        <img src="@/assets/icons/user-cog.svg" alt="Usuarios" class="nav-icon" /> Usuarios
      </router-link>
    </div>
    
    <div class="user-section">
      <div class="user-info" @click="toggleUserMenu">
        <div class="user-avatar">{{ userInitials }}</div>
        <span class="user-name">{{ userName }}</span>
        <img src="@/assets/icons/chevron-down.svg" alt="Abrir menú" class="user-icon" />
      </div>
      <div class="user-menu" v-if="showUserMenu">
        <div class="menu-item" @click="goToProfile">
          <img src="@/assets/icons/user.svg" alt="Perfil" class="menu-icon" /> Perfil
        </div>
        <div class="menu-item" @click="logout">
          <img src="@/assets/icons/log-out.svg" alt="Cerrar sesión" class="menu-icon" /> Cerrar sesión
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
import { mapGetters } from 'vuex';
import eventBus from '@/utils/eventBus';

export default {
  name: 'AppNavigation',
  data() {
    return {
      isExpanded: false,
      showUserMenu: false
    };
  },
  computed: {
    ...mapGetters({
      currentUser: 'auth/currentUser',
      isAuthenticated: 'auth/isAuthenticated',
      userRole: 'auth/userRole'
    }),
    isAdmin() {
      // Por defecto, todos los usuarios que llegan a este punto son admin
      return true;
    },
    hasUserManagementAccess() {
      // Por defecto, todos los usuarios que llegan a este punto tienen acceso a gestión de usuarios
      return true;
    },
    userName() {
      if (!this.currentUser) return 'Admin';
      const firstName = this.currentUser.first_name || '';
      const lastName = this.currentUser.last_name || '';
      return `${firstName} ${lastName}`.trim() || 'Admin';
    },
    userInitials() {
      if (!this.currentUser) return 'A';
      
      const firstName = this.currentUser.first_name || '';
      const lastName = this.currentUser.last_name || '';
      
      if (!firstName && !lastName) return 'A';
      
      const firstInitial = firstName.charAt(0) || '';
      const lastInitial = lastName.charAt(0) || '';
      
      return `${firstInitial}${lastInitial}`.toUpperCase() || 'A';
    }
  },
  methods: {
    toggleNav() {
      this.isExpanded = !this.isExpanded;
      // Emitir el evento usando el eventBus
      eventBus.emit('nav-toggle', this.isExpanded);
      if (this.isExpanded) {
        this.showUserMenu = false;
      }
    },
    toggleUserMenu() {
      this.showUserMenu = !this.showUserMenu;
    },
    goToProfile() {
      this.$router.push('/admin/profile');
      this.showUserMenu = false;
    },
    logout() {
      this.$store.dispatch('auth/logout');
      this.$router.push('/login');
      this.showUserMenu = false;
    },
    closeMenus() {
      this.showUserMenu = false;
    }
  },
  mounted() {
    document.addEventListener('click', (event) => {
      const isClickInsideNav = this.$el.contains(event.target);
      if (!isClickInsideNav) {
        this.closeMenus();
      }
    });
  },
  beforeUnmount() {
    document.removeEventListener('click', this.closeMenus);
  }
};
</script>

<style scoped>
.navigation {
  background-color: #ffffff;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  height: 100vh;
  left: 0;
  position: fixed;
  top: 0;
  transition: all 0.3s ease;
  width: 250px;
  z-index: 1000;
}

.nav-header {
  align-items: center;
  border-bottom: 1px solid #eaeaea;
  display: flex;
  height: 70px;
  justify-content: space-between;
  padding: 0 20px;
}

.logo-container {
  align-items: center;
  display: flex;
}

.logo-image {
  height: 45px;
  width: auto;
}

.toggle-button {
  background: none;
  border: none;
  cursor: pointer;
  display: none;
  flex-direction: column;
  height: 24px;
  justify-content: space-between;
  padding: 0;
  width: 30px;
}

.bar {
  background-color: #333;
  border-radius: 2px;
  height: 3px;
  transition: all 0.3s ease;
  width: 100%;
}

.nav-links {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  padding: 20px 0;
}

.nav-link {
  align-items: center;
  color: #333;
  display: flex;
  padding: 12px 20px;
  text-decoration: none;
  transition: all 0.2s ease;
}

.nav-link i {
  margin-right: 10px;
  width: 20px;
}

.nav-link:hover, .nav-link.router-link-active {
  background-color: rgba(58, 134, 255, 0.1);
  color: #3a86ff;
}

.nav-icon {
  width: 18px;
  height: 18px;
  margin-right: 10px;
  filter: invert(20%) sepia(10%) saturate(2076%) hue-rotate(180deg) brightness(90%) contrast(95%);
}

.nav-link.router-link-active .nav-icon {
  filter: invert(35%) sepia(98%) saturate(1946%) hue-rotate(188deg) brightness(97%) contrast(101%);
}

.user-section {
  border-top: 1px solid #eaeaea;
  padding: 15px 20px;
  position: relative;
}

.user-info {
  align-items: center;
  cursor: pointer;
  display: flex;
}

.user-avatar {
  align-items: center;
  background-color: #3a86ff;
  border-radius: 50%;
  color: white;
  display: flex;
  font-size: 14px;
  font-weight: 600;
  height: 36px;
  justify-content: center;
  margin-right: 10px;
  width: 36px;
}

.user-name {
  flex-grow: 1;
  font-size: 14px;
  font-weight: 500;
}

.user-menu {
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: absolute;
  right: 20px;
  top: 60px;
  width: 180px;
}

.menu-item {
  align-items: center;
  cursor: pointer;
  display: flex;
  padding: 12px 15px;
  transition: background-color 0.2s ease;
}

.menu-item i {
  margin-right: 10px;
  width: 16px;
}

.menu-item:hover {
  background-color: rgba(58, 134, 255, 0.1);
}

.menu-icon {
  width: 16px;
  height: 16px;
  margin-right: 8px;
  filter: invert(20%) sepia(10%) saturate(2076%) hue-rotate(180deg) brightness(90%) contrast(95%);
}

.user-icon {
  width: 14px;
  height: 14px;
  margin-left: 5px;
  filter: invert(20%) sepia(10%) saturate(2076%) hue-rotate(180deg) brightness(90%) contrast(95%);
}

@media (max-width: 768px) {
  .navigation {
    transform: translateX(-100%);
    width: 100%;
  }
  
  .navigation.is-expanded {
    transform: translateX(0);
  }
  
  .toggle-button {
    display: flex;
  }
  
  .nav-header {
    padding: 0 15px;
  }
}
</style>
