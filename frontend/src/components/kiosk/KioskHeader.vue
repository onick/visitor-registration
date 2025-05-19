<template>
  <header class="kiosk-header">
    <div class="header-content">
      <div class="left-section">
        <button 
          v-if="showBackButton" 
          class="back-button" 
          @click="$emit('back')"
          aria-label="Volver"
        >
          <i class="fas fa-arrow-left"></i>
        </button>
        <div class="logo" @click="goToHome">
          <img src="@/assets/images/logo.png" alt="Centro Cultural Banreservas" class="logo-icon" />
          <span class="logo-text">Centro Cultural Banreservas</span>
        </div>
      </div>
      
      <h1 class="page-title">{{ title }}</h1>
      
      <div class="right-section">
        <div class="current-time">{{ currentTime }}</div>
      </div>
    </div>
  </header>
</template>

<script>
export default {
  name: 'KioskHeader',
  props: {
    title: {
      type: String,
      required: true
    },
    showBackButton: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      currentTime: '',
      timeInterval: null
    };
  },
  mounted() {
    this.updateTime();
    this.timeInterval = setInterval(this.updateTime, 1000);
  },
  beforeUnmount() {
    clearInterval(this.timeInterval);
  },
  methods: {
    updateTime() {
      const now = new Date();
      this.currentTime = now.toLocaleTimeString('es-ES', {
        hour: '2-digit',
        minute: '2-digit'
      });
    },
    goToHome() {
      this.$router.push('/kiosk/welcome');
    }
  }
};
</script>

<style scoped>
.kiosk-header {
  background-color: #512da8;
  color: white;
  padding: 1rem 2rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1400px;
  margin: 0 auto;
}

.left-section {
  display: flex;
  align-items: center;
}

.back-button {
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  margin-right: 1.5rem;
  padding: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s;
}

.back-button:hover {
  transform: translateX(-3px);
}

.logo {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.logo-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 0.75rem;
  object-fit: contain;
  background-color: white;
  padding: 4px;
}

.logo-text {
  font-size: 1.2rem;
  font-weight: 500;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
  text-align: center;
  flex: 1;
}

.right-section {
  min-width: 80px;
  text-align: right;
}

.current-time {
  font-size: 1.1rem;
  font-weight: 500;
}

@media (max-width: 768px) {
  .kiosk-header {
    padding: 1rem;
  }
  
  .logo-text {
    display: none;
  }
  
  .page-title {
    font-size: 1.2rem;
  }
}
</style>
