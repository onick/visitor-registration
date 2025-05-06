<template>
  <div class="kiosk-container idle-container">
    <div class="idle-content">
      <img src="../assets/logo.png" alt="Centro Cultural Banreservas" class="idle-logo" />
      
      <div class="idle-message">
        <h1 class="idle-title">{{ translations.title }}</h1>
        <p class="idle-subtitle">{{ translations.subtitle }}</p>
      </div>
      
      <div class="slideshow">
        <div 
          v-for="(slide, index) in slides" 
          :key="index" 
          :class="['slide', { active: currentSlide === index }]"
          :style="{ backgroundImage: `url(${slide.image})` }"
        >
          <div class="slide-content">
            <h2 class="slide-title">{{ slide.title }}</h2>
            <p class="slide-description">{{ slide.description }}</p>
          </div>
        </div>
      </div>
    </div>
    
    <div class="touch-prompt" @click="goHome">
      <div class="touch-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M13 11.5a1.5 1.5 0 0 1 3 0v7.5a1.5 1.5 0 0 1-3 0v-7.5z"></path>
          <path d="M10 13.5a1.5 1.5 0 0 1 3 0v5.5a1.5 1.5 0 0 1-3 0v-5.5z"></path>
          <path d="M7 15.5a1.5 1.5 0 0 1 3 0v3.5a1.5 1.5 0 0 1-3 0v-3.5z"></path>
          <path d="M18 9a3 3 0 0 0-3-3"></path>
          <path d="M18 6a6 6 0 0 0-6-6"></path>
        </svg>
      </div>
      <p class="touch-text">{{ translations.touchPrompt }}</p>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default {
  name: 'IdleView',
  
  setup() {
    const store = useStore()
    const router = useRouter()
    const currentSlide = ref(0)
    const slideInterval = ref(null)
    
    const language = computed(() => store.getters.kioskLanguage)
    
    const translations = computed(() => {
      if (language.value === 'en') {
        return {
          title: 'Welcome to Centro Cultural Banreservas',
          subtitle: 'Explore our cultural events and exhibitions',
          touchPrompt: 'Touch the screen to start'
        }
      } else {
        return {
          title: 'Bienvenido al Centro Cultural Banreservas',
          subtitle: 'Explore nuestros eventos culturales y exposiciones',
          touchPrompt: 'Toque la pantalla para comenzar'
        }
      }
    })
    
    const slides = [
      {
        title: 'Exposiciones Artísticas',
        description: 'Conozca nuestras exposiciones de arte contemporáneo y clásico',
        image: require('../assets/slide1.jpg')
      },
      {
        title: 'Eventos Culturales',
        description: 'Participe en nuestros eventos culturales durante todo el año',
        image: require('../assets/slide2.jpg')
      },
      {
        title: 'Talleres Educativos',
        description: 'Aprenda con nuestros talleres educativos para todas las edades',
        image: require('../assets/slide3.jpg')
      }
    ]
    
    const goHome = () => {
      router.push('/')
    }
    
    const startSlideshow = () => {
      slideInterval.value = setInterval(() => {
        currentSlide.value = (currentSlide.value + 1) % slides.length
      }, 5000)
    }
    
    onMounted(() => {
      startSlideshow()
    })
    
    onBeforeUnmount(() => {
      clearInterval(slideInterval.value)
    })
    
    return {
      translations,
      slides,
      currentSlide,
      goHome
    }
  }
}
</script>

<style scoped>
.idle-container {
  background-color: var(--primary-color);
  color: var(--white);
}

.idle-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  height: 100%;
  padding-top: 50px;
}

.idle-logo {
  max-width: 180px;
  margin-bottom: 20px;
}

.idle-message {
  text-align: center;
  margin-bottom: 40px;
}

.idle-title {
  font-size: 2.5rem;
  margin-bottom: 10px;
}

.idle-subtitle {
  font-size: 1.2rem;
  opacity: 0.9;
}

.slideshow {
  position: relative;
  width: 100%;
  height: 50vh;
  overflow: hidden;
  border-radius: 10px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
}

.slide {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  opacity: 0;
  transition: opacity 1s ease-in-out;
  display: flex;
  align-items: flex-end;
}

.slide.active {
  opacity: 1;
}

.slide-content {
  background: linear-gradient(to top, rgba(0,0,0,0.7), transparent);
  padding: 30px;
  width: 100%;
  color: white;
}

.slide-title {
  font-size: 1.8rem;
  margin-bottom: 10px;
}

.slide-description {
  font-size: 1.1rem;
  opacity: 0.9;
}

.touch-prompt {
  position: fixed;
  bottom: 40px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  animation: pulse 2s infinite;
}

.touch-icon {
  margin-bottom: 10px;
}

.touch-text {
  font-size: 1.2rem;
  font-weight: bold;
}

@keyframes pulse {
  0% {
    transform: translateX(-50%) scale(1);
  }
  50% {
    transform: translateX(-50%) scale(1.05);
  }
  100% {
    transform: translateX(-50%) scale(1);
  }
}
</style>
