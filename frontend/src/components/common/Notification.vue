<template>
  <transition name="notification-fade">
    <div v-if="show" class="notification" :class="notificationClass">
      <div class="notification-icon">
        <i class="fas" :class="iconClass"></i>
      </div>
      <div class="notification-content">
        <div class="notification-message">{{ message }}</div>
      </div>
      <div class="notification-close" @click="close">
        <i class="fas fa-times"></i>
      </div>
    </div>
  </transition>
</template>

<script>
export default {
  name: 'Notification',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    message: {
      type: String,
      default: ''
    },
    type: {
      type: String,
      default: 'info',
      validator: (value) => ['info', 'success', 'warning', 'error'].includes(value)
    },
    duration: {
      type: Number,
      default: 5000
    },
    autoClose: {
      type: Boolean,
      default: true
    }
  },
  data() {
    return {
      timer: null
    };
  },
  computed: {
    notificationClass() {
      return `notification-${this.type}`;
    },
    iconClass() {
      const icons = {
        info: 'fa-info-circle',
        success: 'fa-check-circle',
        warning: 'fa-exclamation-triangle',
        error: 'fa-exclamation-circle'
      };
      return icons[this.type];
    }
  },
  watch: {
    show(newVal) {
      if (newVal && this.autoClose) {
        this.startTimer();
      }
    }
  },
  mounted() {
    if (this.show && this.autoClose) {
      this.startTimer();
    }
  },
  beforeUnmount() {
    this.clearTimer();
  },
  methods: {
    startTimer() {
      this.clearTimer();
      if (this.duration > 0) {
        this.timer = setTimeout(() => {
          this.close();
        }, this.duration);
      }
    },
    clearTimer() {
      if (this.timer) {
        clearTimeout(this.timer);
        this.timer = null;
      }
    },
    close() {
      this.clearTimer();
      this.$emit('update:show', false);
      this.$emit('close');
    }
  }
};
</script>

<style scoped>
.notification {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  display: flex;
  align-items: center;
  min-width: 300px;
  max-width: 450px;
  padding: 15px;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  background-color: #fff;
  color: #333;
  transition: all 0.3s ease;
}

.notification-icon {
  margin-right: 12px;
  font-size: 20px;
}

.notification-content {
  flex: 1;
}

.notification-message {
  font-size: 14px;
  line-height: 1.5;
}

.notification-close {
  margin-left: 12px;
  cursor: pointer;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.notification-close:hover {
  opacity: 1;
}

.notification-info {
  border-left: 4px solid #1890ff;
}

.notification-info .notification-icon {
  color: #1890ff;
}

.notification-success {
  border-left: 4px solid #52c41a;
}

.notification-success .notification-icon {
  color: #52c41a;
}

.notification-warning {
  border-left: 4px solid #faad14;
}

.notification-warning .notification-icon {
  color: #faad14;
}

.notification-error {
  border-left: 4px solid #f5222d;
}

.notification-error .notification-icon {
  color: #f5222d;
}

.notification-fade-enter-active,
.notification-fade-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}

.notification-fade-enter-from,
.notification-fade-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>