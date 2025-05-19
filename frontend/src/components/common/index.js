import AlertMessage from './AlertMessage.vue';
import AppButton from './Button.vue';
import AppCard from './Card.vue';
import DataTable from './DataTable.vue';
import FormField from './FormField.vue';
import AppModal from './Modal.vue';

// Exportar componentes individualmente
export {
  AlertMessage,
  AppButton,
  AppCard,
  DataTable,
  FormField,
  AppModal
};

// Función para instalar todos los componentes como globales en Vue 3
export default {
  install(app) {
    app.component('AlertMessage', AlertMessage);
    app.component('AppButton', AppButton);
    app.component('AppCard', AppCard);
    app.component('DataTable', DataTable);
    app.component('FormField', FormField);
    app.component('AppModal', AppModal);
  }
}; 