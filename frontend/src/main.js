import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import store from './store';
import './plugins/axios'; // Importamos la configuración de axios
import CommonComponents from './components/common';
import './assets/css/main.css';
import './assets/styles/colors.css'; // Importar la paleta de colores
import './assets/styles/theme.css'; // Importar el tema con los colores aplicados
import Toast from 'vue-toastification';
import 'vue-toastification/dist/index.css';
import './assets/styles/toastification.css'; // Estilos personalizados para los toasts

// Crear la aplicación Vue
const app = createApp(App);

// Configurar opciones de Toast
const toastOptions = {
  position: "top-right",
  timeout: 3000,
  closeOnClick: true,
  pauseOnFocusLoss: true,
  pauseOnHover: true,
  draggable: true,
  draggablePercent: 0.6,
  showCloseButtonOnHover: false,
  hideProgressBar: false,
  closeButton: "button",
  icon: true,
  rtl: false,
  transition: "Vue-Toastification__bounce",
  maxToasts: 5,
  newestOnTop: true
};

// Configurar manejador de errores global
app.config.errorHandler = (err, vm, info) => {
  console.error('Error en la aplicación Vue:', err);
  console.error('Componente:', vm);
  console.error('Info:', info);
  // Aquí podrías implementar una lógica para mostrar un mensaje de error amigable
};

// Configurar manejador de advertencias global
app.config.warnHandler = (msg, vm, trace) => {
  console.warn('Advertencia en la aplicación Vue:', msg);
  console.warn('Componente:', vm);
  console.warn('Traza:', trace);
};

// Usar router y store
app.use(router);
app.use(store);
app.use(CommonComponents);
app.use(Toast, toastOptions);

// Montar la aplicación
app.mount('#app');