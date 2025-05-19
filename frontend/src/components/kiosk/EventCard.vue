<template>
  <div class="event-card" @click="$emit('select')">
    <div class="event-date">
      <span class="day">{{ formatDay(event.startDate) }}</span>
      <span class="month">{{ formatMonth(event.startDate) }}</span>
    </div>
    <div class="event-details">
      <h3>{{ event.title }}</h3>
      <p class="event-location">
        <i class="fas fa-map-marker-alt"></i> {{ event.location }}
      </p>
      <p class="event-time">
        <i class="fas fa-clock"></i> {{ formatTime(event.startDate) }} - {{ formatTime(event.endDate) }}
      </p>
      <div class="event-status" :class="getEventStatusClass">
        {{ getEventStatusText }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'EventCard',
  props: {
    event: {
      type: Object,
      required: true
    }
  },
  computed: {
    getEventStatusClass() {
      const now = new Date();
      const startDate = new Date(this.event.startDate);
      const endDate = new Date(this.event.endDate);
      
      if (now >= startDate && now <= endDate) {
        return 'status-ongoing';
      } else if (now < startDate) {
        return 'status-upcoming';
      } else {
        return 'status-past';
      }
    },
    getEventStatusText() {
      const now = new Date();
      const startDate = new Date(this.event.startDate);
      const endDate = new Date(this.event.endDate);
      
      if (now >= startDate && now <= endDate) {
        return 'En curso';
      } else if (now < startDate) {
        return 'Próximamente';
      } else {
        return 'Finalizado';
      }
    }
  },
  methods: {
    formatDay(dateString) {
      const date = new Date(dateString);
      return date.getDate();
    },
    formatMonth(dateString) {
      const date = new Date(dateString);
      const months = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC'];
      return months[date.getMonth()];
    },
    formatTime(dateString) {
      const date = new Date(dateString);
      return date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
    }
  }
};
</script>

<style scoped>
.event-card {
  display: flex;
  background-color: white;
  border-radius: 0.5rem;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.2s;
}

.event-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.15);
}

.event-date {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: #007bff;
  color: white;
  padding: 1rem;
  min-width: 80px;
}

.day {
  font-size: 1.8rem;
  font-weight: bold;
}

.month {
  font-size: 1rem;
  text-transform: uppercase;
}

.event-details {
  padding: 1rem;
  flex: 1;
}

.event-details h3 {
  margin-top: 0;
  margin-bottom: 0.5rem;
  font-size: 1.2rem;
  color: #333;
}

.event-location, .event-time {
  margin: 0.25rem 0;
  font-size: 0.9rem;
  color: #6c757d;
}

.event-status {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.8rem;
  font-weight: bold;
  margin-top: 0.5rem;
}

.status-ongoing {
  background-color: #28a745;
  color: white;
}

.status-upcoming {
  background-color: #fd7e14;
  color: white;
}

.status-past {
  background-color: #6c757d;
  color: white;
}
</style>
