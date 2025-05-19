<template>
  <div class="idle-view">
    <div class="slideshow">
      <div class="slide active">
        <div class="slide-content">
          <div class="logo-container">
            <img src="@/assets/images/logo.png" alt="Centro Cultural Banreservas" class="logo-image">
          </div>
          <p>Sistema de Registro de Visitantes</p>
        </div>
      </div>
    </div>
    
    <div class="footer">
      <p>Toque la pantalla para comenzar</p>
      <div class="time">{{ currentTime }}</div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'IdleView',
  data() {
    return {
      currentTime: '',
      timer: null
    };
  },
  mounted() {
    this.updateTime();
    this.timer = setInterval(this.updateTime, 1000);
    
    document.addEventListener('click', this.handleClick);
    document.addEventListener('touchstart', this.handleClick);
  },
  beforeUnmount() {
    clearInterval(this.timer);
    document.removeEventListener('click', this.handleClick);
    document.removeEventListener('touchstart', this.handleClick);
  },
  methods: {
    updateTime() {
      const now = new Date();
      const hours = now.getHours().toString().padStart(2, '0');
      const minutes = now.getMinutes().toString().padStart(2, '0');
      this.currentTime = `${hours}:${minutes}`;
    },
    handleClick() {
      this.$router.push('/kiosk/welcome');
    }
  }
};
</script>

<style scoped>
.idle-view {
  height: 100vh;
  width: 100vw;
  display: flex;
  flex-direction: column;
  background-color: #f5f5f5;
  overflow: hidden;
}

.slideshow {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.slide {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 1s ease-in-out;
  background: linear-gradient(135deg, #512da8, #140078);
  color: white;
}

.slide.active {
  opacity: 1;
}

.slide-content {
  text-align: center;
  padding: 20px;
}

.slide-content h1 {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.slide-content p {
  font-size: 1.5rem;
  margin-bottom: 2rem;
}

.logo-container {
  width: 250px;
  height: 250px;
  margin: 0 auto 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-image {
  width: 100%;
  height: auto;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.5));
}

.footer {
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer p {
  font-size: 1.2rem;
  margin: 0;
}

.time {
  font-size: 1.5rem;
  font-weight: bold;
}

@media (max-width: 768px) {
  .slide-content p {
    font-size: 1.2rem;
  }
  
  .logo-container {
    width: 180px;
    height: 180px;
    margin-bottom: 20px;
  }
  
  .footer p {
    font-size: 1rem;
  }
  
  .time {
    font-size: 1.2rem;
  }
}
</style>
