<template>
  <header class="kiosk-header">
    <div v-if="showBackButton" class="back-button-container">
      <button @click="goBack" class="back-button">
        <span class="back-icon">←</span> {{ translations.back }}
      </button>
    </div>
    
    <div class="header-content">
      <img 
        :src="logo || defaultLogo" 
        alt="Centro Cultural Banreservas" 
        class="header-logo"
      />
      <div class="header-text">
        <h1 class="header-title">{{ title }}</h1>
        <h2 v-if="subtitle" class="header-subtitle">{{ subtitle }}</h2>
      </div>
    </div>
    
    <div class="language-selector">
      <button 
        @click="changeLanguage('es')" 
        :class="['language-button', language === 'es' ? 'active' : '']"
      >
        ES
      </button>
      <button 
        @click="changeLanguage('en')" 
        :class="['language-button', language === 'en' ? 'active' : '']"
      >
        EN
      </button>
    </div>
  </header>
</template>

<script>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'KioskHeader',
  props: {
    title: {
      type: String,
      required: true
    },
    subtitle: {
      type: String,
      default: ''
    },
    logo: {
      type: String,
      default: ''
    },
    showBackButton: {
      type: Boolean,
      default: false
    },
    language: {
      type: String,
      default: 'es'
    }
  },
  
  setup(props, { emit }) {
    const router = useRouter()
    const defaultLogo = '/images/logo.png'
    
    const translations = computed(() => {
      if (props.language === 'en') {
        return {
          back: 'Back'
        }
      } else {
        return {
          back: 'Regresar'
        }
      }
    })
    
    const goBack = () => {
      router.back()
    }
    
    const changeLanguage = (lang) => {
      emit('change-language', lang)
    }
    
    return {
      defaultLogo,
      translations,
      goBack,
      changeLanguage
    }
  },
  
  emits: ['change-language']
}
</script>

<style scoped>
.kiosk-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: relative;
}

.back-button-container {
  position: absolute;
  left: 20px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 1;
}

.back-button {
  background: none;
  border: none;
  display: flex;
  align-items: center;
  color: var(--primary-color, #006bb3);
  font-size: 1rem;
  cursor: pointer;
  transition: color 0.2s;
}

.back-button:hover {
  color: var(--secondary-color, #00478f);
}

.back-icon {
  font-size: 1.5rem;
  margin-right: 5px;
}

.header-content {
  display: flex;
  align-items: center;
  flex: 1;
  justify-content: center;
}

.header-logo {
  height: 60px;
  margin-right: 15px;
}

.header-title {
  font-size: 1.5rem;
  margin: 0;
  color: var(--primary-color, #006bb3);
}

.header-subtitle {
  font-size: 1rem;
  margin: 5px 0 0 0;
  color: #666;
  font-weight: normal;
}

.language-selector {
  display: flex;
  gap: 5px;
}

.language-button {
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 5px 10px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s;
}

.language-button.active {
  background-color: var(--primary-color, #006bb3);
  color: white;
  border-color: var(--primary-color, #006bb3);
}

@media (max-width: 600px) {
  .kiosk-header {
    flex-direction: column;
    padding: 10px;
  }
  
  .header-content {
    margin-bottom: 10px;
  }
  
  .header-logo {
    height: 40px;
  }
  
  .header-title {
    font-size: 1.2rem;
  }
  
  .back-button-container {
    position: static;
    transform: none;
    margin-bottom: 10px;
  }
}
</style>
