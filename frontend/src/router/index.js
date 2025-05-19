import { createRouter, createWebHistory } from 'vue-router';
import store from '../store';

// Layouts
const AdminLayout = () => import('../layouts/AdminLayout.vue');
const KioskLayout = () => import('../layouts/KioskLayout.vue');

// Vistas Públicas
const Login = () => import('../views/auth/Login.vue');
const ForgotPassword = () => import('../views/auth/ForgotPassword.vue');
const ResetPassword = () => import('../views/auth/ResetPassword.vue');

// Vistas Administrativas
const Dashboard = () => import('../views/admin/Dashboard.vue');
const EventsList = () => import('../views/admin/Events.vue');
const VisitorsList = () => import('../views/admin/Visitors.vue');
const KiosksList = () => import('../views/admin/Kiosks.vue');
const UsersList = () => import('../views/admin/Users.vue');

// Vistas de Kiosco
const IdleView = () => import('../views/IdleView.vue');
const WelcomeView = () => import('../views/WelcomeView.vue');
const RegistrationView = () => import('../views/RegistrationView.vue');
const ConfirmationView = () => import('../views/ConfirmationView.vue');
const CheckinView = () => import('../views/CheckinView.vue');
const EventsView = () => import('../views/EventsView.vue');

const routes = [
  {
    path: '/',
    redirect: '/kiosk/idle'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: ForgotPassword,
    meta: { requiresAuth: false, title: 'Recuperar Contraseña' }
  },
  {
    path: '/reset-password/:token',
    name: 'ResetPassword',
    component: ResetPassword,
    meta: { requiresAuth: false, title: 'Restablecer Contraseña' }
  },
  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/admin/dashboard'
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: Dashboard,
        meta: { title: 'Panel de Control' }
      },
      {
        path: 'events',
        name: 'EventsList',
        component: EventsList,
        meta: { title: 'Gestión de Eventos' }
      },
      {
        path: 'events/:id',
        name: 'EventDetails',
        component: () => import('../views/admin/EventDetails.vue'),
        meta: { title: 'Detalles del Evento' }
      },
      {
        path: 'visitors',
        name: 'VisitorsList',
        component: VisitorsList,
        meta: { title: 'Gestión de Visitantes' }
      },
      {
        path: 'kiosks',
        name: 'KiosksList',
        component: KiosksList,
        meta: { title: 'Gestión de Kioscos' }
      },
      {
        path: 'users',
        name: 'UsersList',
        component: UsersList,
        meta: { title: 'Gestión de Usuarios' }
      }
    ]
  },
  {
    path: '/kiosk',
    component: KioskLayout,
    meta: { requiresAuth: false, isKiosk: true },
    children: [
      {
        path: '',
        redirect: '/kiosk/idle'
      },
      {
        path: 'idle',
        name: 'IdleView',
        component: IdleView,
        meta: { title: 'Bienvenido al Centro Cultural Banreservas' }
      },
      {
        path: 'welcome',
        name: 'WelcomeView',
        component: WelcomeView,
        meta: { title: 'Bienvenido - Centro Cultural Banreservas' }
      },
      {
        path: 'register',
        name: 'RegistrationView',
        component: RegistrationView,
        meta: { title: 'Registro de Visitante' }
      },
      {
        path: 'confirmation',
        name: 'ConfirmationView',
        component: ConfirmationView,
        meta: { title: 'Registro Completado' }
      },
      {
        path: 'checkin',
        name: 'CheckinView',
        component: CheckinView,
        meta: { title: 'Check-in de Visitantes' }
      },
      {
        path: 'events',
        name: 'EventsKioskView',
        component: EventsView,
        meta: { title: 'Eventos' }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/kiosk/idle'
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// Navegación Guard
router.beforeEach((to, from, next) => {
  const isAuthenticated = store.getters['auth/isAuthenticated'];
  
  // Actualizamos el título de la página
  document.title = to.meta.title ? `${to.meta.title} - Centro Cultural Banreservas` : 'Centro Cultural Banreservas';
  
  if (to.matched.some(record => record.meta.requiresAuth)) {
    // Comprobar si la ruta requiere autenticación
    if (!isAuthenticated) {
      next('/login');
    } else {
      next();
    }
  } else {
    // Si la ruta no requiere autenticación
    if (to.path === '/login' && isAuthenticated) {
      next('/admin/dashboard');
    } else {
      next();
    }
  }
});

export default router; 