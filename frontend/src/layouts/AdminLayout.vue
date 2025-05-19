<template>
  <div class="admin-layout">
    <Navigation />
    <div class="content-area" :class="{ 'nav-expanded': isNavExpanded }">
      <div class="content-header">
        <h1 class="page-title">{{ pageTitle }}</h1>
        <div class="breadcrumb">
          <router-link to="/admin/dashboard">Inicio</router-link>
          <span v-if="breadcrumbs.length > 0" class="separator">/</span>
          <template v-for="(crumb, index) in breadcrumbs">
            <router-link :key="index" :to="crumb.path" v-if="index < breadcrumbs.length - 1">
              {{ crumb.name }}
            </router-link>
            <span :key="'sep-' + index" class="separator" v-if="index < breadcrumbs.length - 1">/</span>
            <span :key="'current-' + index" class="current" v-if="index === breadcrumbs.length - 1">
              {{ crumb.name }}
            </span>
          </template>
        </div>
      </div>
      
      <div class="content-body">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script>
import Navigation from '@/components/Navigation.vue';
import eventBus from '@/utils/eventBus';

export default {
  name: 'AdminLayout',
  components: {
    Navigation
  },
  data() {
    return {
      isNavExpanded: false
    };
  },
  computed: {
    pageTitle() {
      return this.$route.meta?.title || 'Dashboard';
    },
    breadcrumbs() {
      const breadcrumbs = [];
      const { matched } = this.$route;
      
      matched.forEach((route) => {
        if (route.meta && route.meta.breadcrumb) {
          breadcrumbs.push({
            name: route.meta.breadcrumb,
            path: route.path
          });
        }
      });
      
      return breadcrumbs;
    }
  },
  watch: {
    $route() {
      // Close mobile navigation when route changes
      this.isNavExpanded = false;
    }
  },
  mounted() {
    // Escuchar eventos de navegación usando el eventBus
    eventBus.on('nav-toggle', this.handleNavToggle);
  },
  beforeUnmount() {
    // Limpiar los listeners de eventos
    eventBus.off('nav-toggle', this.handleNavToggle);
  },
  methods: {
    // Manejar el evento de navegación
    handleNavToggle(expanded) {
      this.isNavExpanded = expanded;
    }
  }
};
</script>

<style scoped>
.admin-layout {
  display: flex;
  height: 100vh;
  width: 100%;
}

.content-area {
  background-color: var(--color-background-light);
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  margin-left: 250px;
  overflow-x: hidden;
  transition: margin-left 0.3s ease;
}

.content-header {
  background-color: var(--color-background);
  border-bottom: 1px solid var(--border-color);
  padding: 20px 30px;
}

.page-title {
  color: var(--color-dark);
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 10px 0;
}

.breadcrumb {
  color: var(--color-text-light);
  display: flex;
  font-size: 14px;
}

.breadcrumb a {
  color: var(--color-secondary);
  text-decoration: none;
  transition: color 0.2s;
}

.breadcrumb a:hover {
  color: var(--color-secondary-dark);
}

.breadcrumb .separator {
  margin: 0 8px;
  color: var(--color-dark-lighter);
}

.breadcrumb .current {
  color: var(--color-dark);
  font-weight: 500;
}

.content-body {
  flex-grow: 1;
  overflow-y: auto;
  padding: 30px;
}

@media (max-width: 768px) {
  .content-area {
    margin-left: 0;
  }
  
  .content-area.nav-expanded {
    margin-left: 100vw;
  }
  
  .content-header {
    padding: 15px 20px;
  }
  
  .content-body {
    padding: 20px;
  }
}
</style>
