<template>
  <div class="virtual-keyboard-wrapper">
    <div class="keyboard-header">
      <button @click="$emit('close')" class="keyboard-close-btn">
        <span class="close-icon">×</span> {{ translations.close }}
      </button>
    </div>
    
    <div v-if="type === 'email'" class="email-shortcuts">
      <button 
        v-for="(shortcut, index) in emailShortcuts" 
        :key="index"
        @click="$emit('input', shortcut)" 
        class="email-shortcut-btn"
      >
        {{ shortcut }}
      </button>
    </div>
    
    <div class="keyboard-layout">
      <div class="keyboard-row">
        <button 
          v-for="key in '1234567890'"
          :key="key"
          @click="$emit('input', key)" 
          class="keyboard-key"
        >
          {{ key }}
        </button>
      </div>
      
      <div class="keyboard-row">
        <button 
          v-for="key in 'qwertyuiop'"
          :key="key"
          @click="$emit('input', key)" 
          class="keyboard-key"
        >
          {{ key }}
        </button>
      </div>
      
      <div class="keyboard-row">
        <button 
          v-for="key in 'asdfghjklñ'"
          :key="key"
          @click="$emit('input', key)" 
          class="keyboard-key"
        >
          {{ key }}
        </button>
      </div>
      
      <div class="keyboard-row">
        <button 
          v-for="key in 'zxcvbnm'"
          :key="key"
          @click="$emit('input', key)" 
          class="keyboard-key"
        >
          {{ key }}
        </button>
        <button 
          @click="$emit('delete')" 
          class="keyboard-key keyboard-key-function"
        >
          ← {{ translations.delete }}
        </button>
      </div>
      
      <div class="keyboard-row">
        <button 
          v-if="type === 'email'" 
          @click="$emit('input', '@')" 
          class="keyboard-key keyboard-key-function"
        >
          @
        </button>
        <button 
          v-if="type === 'email'" 
          @click="$emit('input', '.')" 
          class="keyboard-key keyboard-key-function"
        >
          .
        </button>
        <button 
          v-if="type === 'phone'"
          @click="$emit('input', '+')" 
          class="keyboard-key keyboard-key-function"
        >
          +
        </button>
        <button 
          v-if="type === 'phone'"
          @click="$emit('input', '-')" 
          class="keyboard-key keyboard-key-function"
        >
          -
        </button>
        <button 
          @click="$emit('input', ' ')"
          class="keyboard-key keyboard-key-space"
        >
          {{ translations.space }}
        </button>
        <button 
          @click="$emit('close')"
          class="keyboard-key keyboard-key-function keyboard-key-done"
        >
          {{ translations.done }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'VirtualKeyboard',
  props: {
    type: {
      type: String,
      default: 'text',
      validator: (value) => ['text', 'email', 'phone'].includes(value)
    },
    language: {
      type: String,
      default: 'es'
    }
  },
  
  setup(props) {
    const translations = computed(() => {
      if (props.language === 'en') {
        return {
          close: 'Close Keyboard',
          delete: 'Delete',
          space: 'Space',
          done: 'Done'
        }
      } else {
        return {
          close: 'Cerrar Teclado',
          delete: 'Borrar',
          space: 'Espacio',
          done: 'Listo'
        }
      }
    })
    
    const emailShortcuts = [
      '@gmail.com',
      '@hotmail.com',
      '@outlook.com',
      '@yahoo.com'
    ]
    
    return {
      translations,
      emailShortcuts
    }
  },
  
  emits: ['input', 'delete', 'close']
}
</script>

<style scoped>
.virtual-keyboard-wrapper {
  background-color: #f0f0f0;
  border-top: 1px solid #ccc;
  padding: 10px;
  width: 100%;
  box-sizing: border-box;
}

.keyboard-header {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 10px;
}

.keyboard-close-btn {
  background: none;
  border: none;
  color: #666;
  font-size: 0.9rem;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.close-icon {
  font-size: 1.2rem;
  margin-right: 5px;
}

.email-shortcuts {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

.email-shortcut-btn {
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 8px 12px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.email-shortcut-btn:hover, .email-shortcut-btn:active {
  background-color: #eee;
}

.keyboard-layout {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.keyboard-row {
  display: flex;
  justify-content: center;
  gap: 8px;
}

.keyboard-key {
  flex: 1;
  min-width: 40px;
  height: 50px;
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 6px;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 1.1rem;
  cursor: pointer;
  user-select: none;
  transition: all 0.1s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.keyboard-key:active {
  transform: translateY(2px);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  background-color: #eee;
}

.keyboard-key-function {
  min-width: 70px;
  font-size: 0.9rem;
  background-color: #eee;
}

.keyboard-key-space {
  flex: 3;
  min-width: 150px;
}

.keyboard-key-done {
  background-color: var(--primary-color, #006bb3);
  color: white;
  font-weight: bold;
}
</style>
