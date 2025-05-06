<template>
  <div class="kiosk-container">
    <div class="kiosk-header">
      <h1 class="kiosk-title">{{ translations.registerTitle }}</h1>
      <h2 class="kiosk-subtitle" v-if="selectedEvent">
        {{ selectedEvent.title }}
      </h2>
    </div>
    
    <div class="kiosk-content">
      <div v-if="!selectedEvent" class="kiosk-message kiosk-message-error">
        {{ translations.noEventSelected }}
        <button @click="goToEvents" class="kiosk-button">
          {{ translations.selectEvent }}
        </button>
      </div>
      
      <form v-else class="kiosk-form" @submit.prevent="submitForm">
        <div class="form-description">
          {{ translations.formDescription }}
        </div>
        
        <div class="kiosk-form-group">
          <label for="name" class="kiosk-label">{{ translations.nameLabel }} *</label>
          <input
            type="text"
            id="name"
            v-model="visitorData.name"
            class="kiosk-input"
            :placeholder="translations.namePlaceholder"
            required
            @focus="activeInput = 'name'"
          >
        </div>
        
        <div class="kiosk-form-group">
          <label for="email" class="kiosk-label">{{ translations.emailLabel }}</label>
          <input
            type="email"
            id="email"
            v-model="visitorData.email"
            class="kiosk-input"
            :placeholder="translations.emailPlaceholder"
            @focus="activeInput = 'email'"
          >
        </div>
        
        <div class="kiosk-form-group">
          <label for="phone" class="kiosk-label">{{ translations.phoneLabel }}</label>
          <input
            type="tel"
            id="phone"
            v-model="visitorData.phone"
            class="kiosk-input"
            :placeholder="translations.phonePlaceholder"
            @focus="activeInput = 'phone'"
          >
        </div>
        
        <div v-if="error" class="kiosk-message kiosk-message-error">
          {{ error }}
        </div>
        
        <div class="form-buttons">
          <button 
            type="button" 
            @click="goBack" 
            class="kiosk-button kiosk-button-secondary"
          >
            {{ translations.back }}
          </button>
          
          <button 
            type="submit" 
            class="kiosk-button"
            :disabled="!visitorData.name || isLoading"
          >
            <span v-if="isLoading" class="loader-small"></span>
            <span v-else>{{ translations.submit }}</span>
          </button>
        </div>
      </form>
      
      <!-- Teclado virtual -->
      <div v-if="activeInput" class="virtual-keyboard-container">
        <div class="virtual-keyboard-header">
          <button @click="closeKeyboard" class="keyboard-close">
            × {{ translations.closeKeyboard }}
          </button>
        </div>
        
        <div v-if="activeInput === 'email'" class="keyboard-email-shortcuts">
          <button @click="addToInput('@gmail.com')" class="keyboard-shortcut">@gmail.com</button>
          <button @click="addToInput('@hotmail.com')" class="keyboard-shortcut">@hotmail.com</button>
          <button @click="addToInput('@outlook.com')" class="keyboard-shortcut">@outlook.com</button>
        </div>
        
        <div class="virtual-keyboard">
          <!-- Filas del teclado -->
          <div class="keyboard-row">
            <button 
              v-for="key in '1234567890'"
              :key="key"
              @click="addToInput(key)"
              class="keyboard-key"
            >
              {{ key }}
            </button>
          </div>
          
          <div class="keyboard-row">
            <button 
              v-for="key in 'qwertyuiop'"
              :key="key"
              @click="addToInput(key)"
              class="keyboard-key"
            >
              {{ key }}
            </button>
          </div>
          
          <div class="keyboard-row">
            <button 
              v-for="key in 'asdfghjklñ'"
              :key="key"
              @click="addToInput(key)"
              class="keyboard-key"
            >
              {{ key }}
            </button>
          </div>
          
          <div class="keyboard-row">
            <button 
              v-for="key in 'zxcvbnm'"
              :key="key"
              @click="addToInput(key)"
              class="keyboard-key"
            >
              {{ key }}
            </button>
            <button @click="deleteFromInput" class="keyboard-key keyboard-key-wide">
              ← {{ translations.delete }}
            </button>
          </div>
          
          <div class="keyboard-row">
            <button 
              v-if="activeInput === 'email'"
              @click="addToInput('@')"
              class="keyboard-key keyboard-key-wide"
            >
              @
            </button>
            <button 
              v-if="activeInput === 'email'"
              @click="addToInput('.')"
              class="keyboard-key keyboard-key-wide"
            >
              .
            </button>
            <button 
              @click="addToInput(' ')"
              class="keyboard-key keyboard-key-space"
            >
              {{ translations.space }}
            </button>
            <button 
              @click="closeKeyboard"
              class="keyboard-key keyboard-key-wide keyboard-key-action"
            >
              {{ translations.done }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useStore } from 'vuex'
import { useRouter, useRoute } from 'vue-router'

export default {
  name: 'RegistrationView',
  props: {
    eventId: {
      type: String,
      required: true
    }
  },
  
  setup(props) {
    const store = useStore()
    const router = useRouter()
    const route = useRoute()
    
    const activeInput = ref(null)
    
    const selectedEvent = computed(() => store.state.selectedEvent)
    const isLoading = computed(() => store.state.isLoading)
    const error = computed(() => store.state.error)
    const language = computed(() => store.getters.kioskLanguage)
    
    const visitorData = ref({
      name: '',
      email: '',
      phone: ''
    })
    
    const translations = computed(() => {
      if (language.value === 'en') {
        return {
          registerTitle: 'Register your Attendance',
          formDescription: 'Please provide your information to register for this event.',
          nameLabel: 'Full Name',
          namePlaceholder: 'Enter your full name',
          emailLabel: 'Email (optional)',
          emailPlaceholder: 'Enter your email',
          phoneLabel: 'Phone (optional)',
          phonePlaceholder: 'Enter your phone number',
          submit: 'Register',
          back: 'Go Back',
          noEventSelected: 'No event selected.',
          selectEvent: 'Select an Event',
          delete: 'Delete',
          space: 'Space',
          done: 'Done',
          closeKeyboard: 'Close Keyboard'
        }
      } else {
        return {
          registerTitle: 'Registre su Asistencia',
          formDescription: 'Por favor proporcione su información para registrarse en este evento.',
          nameLabel: 'Nombre Completo',
          namePlaceholder: 'Ingrese su nombre completo',
          emailLabel: 'Correo Electrónico (opcional)',
          emailPlaceholder: 'Ingrese su correo electrónico',
          phoneLabel: 'Teléfono (opcional)',
          phonePlaceholder: 'Ingrese su número de teléfono',
          submit: 'Registrarse',
          back: 'Regresar',
          noEventSelected: 'Ningún evento seleccionado.',
          selectEvent: 'Seleccionar un Evento',
          delete: 'Borrar',
          space: 'Espacio',
          done: 'Listo',
          closeKeyboard: 'Cerrar Teclado'
        }
      }
    })
    
    // Verificar el evento seleccionado
    onMounted(async () => {
      if (!selectedEvent.value && props.eventId) {
        // Si no hay evento seleccionado, intentar cargar los eventos
        try {
          await store.dispatch('fetchActiveEvents')
          const event = store.state.activeEvents.find(e => e.id.toString() === props.eventId)
          if (event) {
            store.dispatch('selectEvent', event)
          }
        } catch (err) {
          console.error(err)
        }
      }
    })
    
    const submitForm = async () => {
      if (!visitorData.value.name) {
        return
      }
      
      try {
        // Actualizar los datos del visitante en el store
        store.commit('SET_VISITOR_DATA', visitorData.value)
        
        // Registrar al visitante
        await store.dispatch('registerVisitor')
        
        // Redirigir a la página de confirmación
        router.push('/confirmation')
      } catch (err) {
        console.error(err)
      }
    }
    
    const goBack = () => {
      router.push('/events')
    }
    
    const goToEvents = () => {
      router.push('/events')
    }
    
    const addToInput = (key) => {
      if (activeInput.value) {
        visitorData.value[activeInput.value] += key
      }
    }
    
    const deleteFromInput = () => {
      if (activeInput.value) {
        visitorData.value[activeInput.value] = visitorData.value[activeInput.value].slice(0, -1)
      }
    }
    
    const closeKeyboard = () => {
      activeInput.value = null
    }
    
    return {
      selectedEvent,
      isLoading,
      error,
      visitorData,
      translations,
      activeInput,
      submitForm,
      goBack,
      goToEvents,
      addToInput,
      deleteFromInput,
      closeKeyboard
    }
  }
}
</script>

<style scoped>
.form-description {
  margin-bottom: 20px;
  color: var(--dark-gray);
}

.form-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 30px;
}

.loader-small {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255,255,255,0.3);
  border-radius: 50%;
  border-top-color: var(--white);
  animation: spin 1s ease-in-out infinite;
}

.virtual-keyboard-container {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  background-color: var(--light-gray);
  box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
  z-index: 1000;
  padding: 15px;
  box-sizing: border-box;
}

.virtual-keyboard-header {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 10px;
}

.keyboard-close {
  background: none;
  border: none;
  color: var(--dark-gray);
  font-size: 1rem;
  cursor: pointer;
}

.keyboard-row {
  display: flex;
  justify-content: center;
  margin-bottom: 10px;
}

.keyboard-key {
  background-color: var(--white);
  border: 1px solid var(--medium-gray);
  border-radius: 5px;
  padding: 15px;
  margin: 0 5px;
  font-size: 1.2rem;
  min-width: 40px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.keyboard-key:active {
  background-color: var(--medium-gray);
}

.keyboard-key-wide {
  min-width: 80px;
}

.keyboard-key-space {
  min-width: 200px;
}

.keyboard-key-action {
  background-color: var(--primary-color);
  color: var(--white);
}

.keyboard-email-shortcuts {
  display: flex;
  justify-content: center;
  margin-bottom: 10px;
}

.keyboard-shortcut {
  background-color: var(--white);
  border: 1px solid var(--medium-gray);
  border-radius: 5px;
  padding: 10px 15px;
  margin: 0 5px;
  font-size: 1rem;
  cursor: pointer;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
