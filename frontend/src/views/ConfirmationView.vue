<template>
  <div class="kiosk-container">
    <div class="kiosk-header">
      <h1 class="kiosk-title">{{ translations.title }}</h1>
    </div>
    
    <div class="kiosk-content">
      <div class="confirmation-container">
        <div class="confirmation-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
            <polyline points="22 4 12 14.01 9 11.01"></polyline>
          </svg>
        </div>
        
        <h2 class="confirmation-message">{{ translations.successMessage }}</h2>
        
        <div class="event-details" v-if="selectedEvent">
          <p class="event-title">{{ selectedEvent.title }}</p>
          <p class="event-location">{{ selectedEvent.location }}</p>
          <p class="event-time">{{ formatEventTime(selectedEvent) }}</p>
        </div>
        
        <p class="confirmation-instruction">{{ translations.instruction }}</p>
        
        <div class="countdown">{{ countdown }}</div>
      </div>
    </div>
    
    <div class="kiosk-footer">
      <button @click="goHome" class="kiosk-button">
        {{ translations.done }}
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default {
  name: 'ConfirmationView',
  
  setup() {
    const store = useStore()
    const router = useRouter()
    
    const selectedEvent = computed(() => store.state.selectedEvent)
    const language = computed(() => store.getters.kioskLanguage)
    const countdown = ref(10)
    const timer = ref(null)
    
    const translations = computed(() => {
      if (language.value === 'en') {
        return {
          title: 'Registration Complete',
          successMessage: 'Thank you for registering!',
          instruction: 'You will be redirected to the home screen in',
          done: 'Return to Home',
          seconds: 'seconds'
        }
      } else {
        return {
          title: 'Registro Completado',
          successMessage: '¡Gracias por registrarse!',
          instruction: 'Será redirigido a la pantalla de inicio en',
          done: 'Volver al Inicio',
          seconds: 'segundos'
        }
      }
    })
    
    const formatEventTime = (event) => {
      const start = new Date(event.start_date)
      const end = new Date(event.end_date)
      
      // Formato de fecha
      const dateOptions = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }
      const timeOptions = { hour: '2-digit', minute: '2-digit' }
      
      const dateStr = start.toLocaleDateString(language.value === 'en' ? 'en-US' : 'es-ES', dateOptions)
      const startTimeStr = start.toLocaleTimeString(language.value === 'en' ? 'en-US' : 'es-ES', timeOptions)
      const endTimeStr = end.toLocaleTimeString(language.value === 'en' ? 'en-US' : 'es-ES', timeOptions)
      
      return `${dateStr}, ${startTimeStr} - ${endTimeStr}`
    }
    
    const goHome = () => {
      clearInterval(timer.value)
      store.dispatch('reset')
      router.push('/')
    }
    
    onMounted(() => {
      // Iniciar cuenta regresiva
      timer.value = setInterval(() => {
        countdown.value--
        
        if (countdown.value <= 0) {
          clearInterval(timer.value)
          goHome()
        }
      }, 1000)
    })
    
    onBeforeUnmount(() => {
      clearInterval(timer.value)
    })
    
    return {
      selectedEvent,
      translations,
      countdown,
      formatEventTime,
      goHome
    }
  }
}
</script>

<style scoped>
.confirmation-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background-color: var(--white);
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  max-width: 600px;
  width: 100%;
}

.confirmation-icon {
  color: var(--success-color);
  margin-bottom: 20px;
}

.confirmation-message {
  font-size: 2rem;
  color: var(--primary-color);
  margin-bottom: 20px;
}

.event-details {
  margin: 20px 0;
  padding: 15px;
  background-color: var(--light-gray);
  border-radius: 8px;
  width: 100%;
  text-align: center;
}

.event-title {
  font-size: 1.3rem;
  font-weight: bold;
  margin-bottom: 10px;
}

.event-location {
  color: var(--dark-gray);
  margin-bottom: 5px;
}

.event-time {
  color: var(--primary-color);
}

.confirmation-instruction {
  margin: 20px 0 10px;
  color: var(--dark-gray);
}

.countdown {
  font-size: 2rem;
  font-weight: bold;
  color: var(--primary-color);
  margin-bottom: 20px;
}

.kiosk-footer {
  margin-top: 30px;
}
</style>
