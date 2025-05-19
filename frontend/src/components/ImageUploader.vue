<template>
  <div class="image-uploader">
    <div v-if="imageUrl" class="image-preview">
      <img :src="fullImageUrl" :alt="altText" />
      <div class="image-actions">
        <button 
          @click="removeImage" 
          class="btn-remove"
          :disabled="isLoading"
          v-if="!readonly"
        >
          <i class="fas fa-trash"></i>
          Eliminar
        </button>
      </div>
    </div>
    
    <div v-else class="upload-area" :class="{ 'dragging': isDragging }">
      <input
        type="file"
        ref="fileInput"
        @change="handleFileSelect"
        accept="image/*"
        style="display: none"
      />
      
      <div
        @drop="handleDrop"
        @dragover.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
        @click="$refs.fileInput.click()"
        class="drop-zone"
      >
        <i class="fas fa-cloud-upload-alt"></i>
        <p>Arrastra una imagen aquí o haz clic para seleccionar</p>
        <span class="file-info">JPG, PNG, GIF o WebP - Max 5MB</span>
      </div>
    </div>
    
    <div v-if="isLoading" class="loading-overlay">
      <i class="fas fa-circle-notch fa-spin"></i>
      <p>{{ loadingText }}</p>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import NotificationService from '@/services/notificationService'

export default {
  name: 'ImageUploader',
  props: {
    eventId: {
      type: Number,
      required: true
    },
    currentImageUrl: {
      type: String,
      default: null
    },
    altText: {
      type: String,
      default: 'Imagen del evento'
    },
    readonly: {
      type: Boolean,
      default: false
    }
  },
  setup(props, { emit }) {
    const fileInput = ref(null)
    const isLoading = ref(false)
    const loadingText = ref('Subiendo imagen...')
    const isDragging = ref(false)
    const imageUrl = ref(props.currentImageUrl)

    const fullImageUrl = computed(() => {
      if (!imageUrl.value) return null
      
      // Si la URL ya es completa, devuélvela tal cual
      if (imageUrl.value.startsWith('http')) {
        return imageUrl.value
      }
      
      // Si es una ruta relativa, construye la URL completa
      return `${process.env.VUE_APP_API_URL}${imageUrl.value}`
    })

    const validateFile = (file) => {
      const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
      const maxSize = 5 * 1024 * 1024 // 5MB

      if (!allowedTypes.includes(file.type)) {
        NotificationService.error('Tipo de archivo no permitido. Solo se aceptan JPG, PNG, GIF y WebP')
        return false
      }

      if (file.size > maxSize) {
        NotificationService.error('El archivo es demasiado grande. Máximo 5MB')
        return false
      }

      return true
    }

    const uploadImage = async (file) => {
      if (!validateFile(file)) return

      isLoading.value = true
      loadingText.value = 'Subiendo imagen...'

      const formData = new FormData()
      formData.append('image', file)

      try {
        // Obtener token de autenticación
        const token = localStorage.getItem('auth_token') || 'token-de-ejemplo'

        const response = await fetch(
          `${process.env.VUE_APP_API_URL}/events/${props.eventId}/upload-image`,
          {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`
            },
            body: formData
          }
        )

        if (!response.ok) {
          const error = await response.json()
          throw new Error(error.error || 'Error al subir la imagen')
        }

        const data = await response.json()
        imageUrl.value = data.image_url
        
        NotificationService.success('Imagen subida exitosamente')
        emit('image-uploaded', data.image_url)
      } catch (error) {
        console.error('Error al subir imagen:', error)
        NotificationService.error(error.message || 'Error al subir la imagen')
      } finally {
        isLoading.value = false
      }
    }

    const removeImage = async () => {
      isLoading.value = true
      loadingText.value = 'Eliminando imagen...'

      try {
        // Obtener token de autenticación
        const token = localStorage.getItem('auth_token') || 'token-de-ejemplo'

        const response = await fetch(
          `${process.env.VUE_APP_API_URL}/events/${props.eventId}/remove-image`,
          {
            method: 'DELETE',
            headers: {
              'Authorization': `Bearer ${token}`
            }
          }
        )

        if (!response.ok) {
          const error = await response.json()
          throw new Error(error.error || 'Error al eliminar la imagen')
        }

        imageUrl.value = null
        NotificationService.success('Imagen eliminada exitosamente')
        emit('image-removed')
      } catch (error) {
        console.error('Error al eliminar imagen:', error)
        NotificationService.error(error.message || 'Error al eliminar la imagen')
      } finally {
        isLoading.value = false
      }
    }

    const handleFileSelect = (event) => {
      const file = event.target.files[0]
      if (file) {
        uploadImage(file)
      }
    }

    const handleDrop = (event) => {
      event.preventDefault()
      isDragging.value = false
      
      const file = event.dataTransfer.files[0]
      if (file) {
        uploadImage(file)
      }
    }

    return {
      fileInput,
      isLoading,
      loadingText,
      isDragging,
      imageUrl,
      fullImageUrl,
      removeImage,
      handleFileSelect,
      handleDrop
    }
  }
}
</script>

<style scoped>
.image-uploader {
  position: relative;
  width: 100%;
  max-width: 500px;
  margin: 0 auto;
}

.image-preview {
  position: relative;
  width: 100%;
  border-radius: 8px;
  overflow: hidden;
  background-color: #f8f9fa;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.image-preview img {
  width: 100%;
  height: auto;
  display: block;
}

.image-actions {
  position: absolute;
  top: 10px;
  right: 10px;
}

.btn-remove {
  background-color: rgba(220, 53, 69, 0.9);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.btn-remove:hover {
  background-color: rgba(220, 53, 69, 1);
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.btn-remove:disabled {
  background-color: rgba(108, 117, 125, 0.6);
  cursor: not-allowed;
  transform: none;
}

.upload-area {
  width: 100%;
  border: 2px dashed #dee2e6;
  border-radius: 8px;
  transition: all 0.3s;
}

.upload-area.dragging {
  border-color: #F99D2A;
  background-color: rgba(249, 157, 42, 0.05);
}

.drop-zone {
  padding: 60px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}

.drop-zone:hover {
  background-color: #f8f9fa;
}

.drop-zone i {
  font-size: 48px;
  color: #6c757d;
  margin-bottom: 16px;
}

.drop-zone p {
  font-size: 16px;
  color: #495057;
  margin: 0 0 8px;
  font-weight: 500;
}

.file-info {
  font-size: 14px;
  color: #6c757d;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  border-radius: 8px;
  z-index: 10;
}

.loading-overlay i {
  font-size: 32px;
  color: #F99D2A;
}

.loading-overlay p {
  font-size: 16px;
  color: #495057;
  margin: 0;
  font-weight: 500;
}

@media (max-width: 576px) {
  .drop-zone {
    padding: 40px 15px;
  }
  
  .drop-zone i {
    font-size: 36px;
  }
  
  .drop-zone p {
    font-size: 14px;
  }
  
  .file-info {
    font-size: 12px;
  }
}
</style>
