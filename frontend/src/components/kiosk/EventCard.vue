<template>
  <div class="event-card" @click="$emit('select')">
    <div class="event-image-container">
      <img 
        :src="event.image_url || defaultImage" 
        :alt="event.title"
        class="event-image"
      />
      <div v-if="isActive" class="event-active-badge">
        {{ translations.now }}
      </div>
    </div>
    <div class="event-info">
      <h3 class="event-title">{{ event.title }}</h3>
      <p class="event-location">
        <span class="location-icon">📍</span> {{ event.location }}
      </p>
      <p class="event-time">
        <span class="time-icon">🕒</span> {{ formattedTime }}
      </p>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'EventCard',
  props: {
    event: {
      type: Object,
      required: true
    },
    language: {
      type: String,
      default: 'es'
    }
  },
  
  setup(props) {
    // Ruta relativa para imagen por defecto
    const defaultImage = '/images/event-placeholder.jpg'
    
    const translations = computed(() => {
      if (props.language === 'en') {
        return {
          now: 'Happening Now'
        }
      } else {
        return {
          now: 'En Curso'
        }
      }
    })
    
    const formattedTime = computed(() => {
      const start = new Date(props.event.start_date)
      const end = new Date(props.event.end_date)
      
      // Opciones para el formato de tiempo
      const options = { hour: '2-digit', minute: '2-digit' }
      
      // Formatear hora de inicio
      return start.toLocaleTimeString(props.language === 'en' ? 'en-US' : 'es-ES', options)
    })
    
    const isActive = computed(() => {
      const now = new Date()
      const start = new Date(props.event.start_date)
      const end = new Date(props.event.end_date)
      
      return start <= now && end >= now
    })
    
    return {
      defaultImage,
      translations,
      formattedTime,
      isActive
    }
  },
  
  emits: ['select']
}
</script>

<style scoped>
.event-card {
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s, box-shadow 0.3s;
  cursor: pointer;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.event-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.event-image-container {
  position: relative;
  height: 160px;
  overflow: hidden;
}

.event-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s;
}

.event-card:hover .event-image {
  transform: scale(1.05);
}

.event-active-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: #ff6b6b;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: bold;
}

.event-info {
  padding: 15px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.event-title {
  font-size: 1.2rem;
  margin: 0 0 10px 0;
  color: var(--primary-color, #006bb3);
  line-height: 1.3;
}

.event-location, .event-time {
  margin: 5px 0;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
}

.event-location {
  color: #666;
}

.event-time {
  color: #333;
  font-weight: bold;
  margin-top: auto;
}

.location-icon, .time-icon {
  margin-right: 5px;
  font-size: 1rem;
}
</style>
