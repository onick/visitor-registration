<template>
  <div class="users-view">
    <h1>Gestión de Usuarios</h1>
    <p>Administración de usuarios del sistema</p>
    
    <div class="actions-bar">
      <div class="search-box">
        <input type="text" placeholder="Buscar usuarios..." v-model="searchTerm">
      </div>
      <button class="btn btn-primary">
        <i class="fas fa-plus"></i> Nuevo Usuario
      </button>
    </div>
    
    <div class="table-container">
      <table class="users-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Nombre</th>
            <th>Email</th>
            <th>Rol</th>
            <th>Estado</th>
            <th>Último acceso</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in filteredUsers" :key="user.id">
            <td>{{ user.id }}</td>
            <td>
              <div class="user-info">
                <div class="user-avatar" :style="{ backgroundColor: getAvatarColor(user.username) }">
                  {{ getInitials(user.firstName, user.lastName) }}
                </div>
                <div>
                  <div class="user-name">{{ user.firstName }} {{ user.lastName }}</div>
                  <div class="user-username">@{{ user.username }}</div>
                </div>
              </div>
            </td>
            <td>{{ user.email }}</td>
            <td>
              <span class="role-badge" :class="'role-' + user.role.toLowerCase()">
                {{ getRoleName(user.role) }}
              </span>
            </td>
            <td>
              <span class="status-badge" :class="user.active ? 'status-active' : 'status-inactive'">
                {{ user.active ? 'Activo' : 'Inactivo' }}
              </span>
            </td>
            <td>{{ formatDate(user.lastLogin) }}</td>
            <td class="actions-cell">
              <button class="btn-icon" title="Editar">
                <i class="fas fa-edit"></i>
              </button>
              <button class="btn-icon" title="Cambiar contraseña">
                <i class="fas fa-key"></i>
              </button>
              <button class="btn-icon" :class="user.active ? 'delete' : 'restore'" :title="user.active ? 'Desactivar' : 'Activar'">
                <i :class="user.active ? 'fas fa-user-slash' : 'fas fa-user-check'"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
export default {
  name: 'UsersList',
  data() {
    return {
      searchTerm: '',
      users: [
        {
          id: 1,
          firstName: 'Admin',
          lastName: 'Usuario',
          username: 'admin',
          email: 'admin@centroculturalbanreservas.com',
          role: 'ADMIN',
          active: true,
          lastLogin: '2023-12-18T16:30:00'
        },
        {
          id: 2,
          firstName: 'María',
          lastName: 'Rodríguez',
          username: 'mrodriguez',
          email: 'maria.rodriguez@centroculturalbanreservas.com',
          role: 'STAFF',
          active: true,
          lastLogin: '2023-12-18T14:15:00'
        },
        {
          id: 3,
          firstName: 'José',
          lastName: 'Pérez',
          username: 'jperez',
          email: 'jose.perez@centroculturalbanreservas.com',
          role: 'STAFF',
          active: true,
          lastLogin: '2023-12-17T09:45:00'
        },
        {
          id: 4,
          firstName: 'Ana',
          lastName: 'García',
          username: 'agarcia',
          email: 'ana.garcia@centroculturalbanreservas.com',
          role: 'MANAGER',
          active: false,
          lastLogin: '2023-12-15T11:20:00'
        },
        {
          id: 5,
          firstName: 'Carlos',
          lastName: 'Martínez',
          username: 'cmartinez',
          email: 'carlos.martinez@centroculturalbanreservas.com',
          role: 'VIEWER',
          active: true,
          lastLogin: '2023-12-18T15:10:00'
        }
      ]
    };
  },
  computed: {
    filteredUsers() {
      if (!this.searchTerm) return this.users;
      
      const term = this.searchTerm.toLowerCase();
      return this.users.filter(user => 
        user.firstName.toLowerCase().includes(term) ||
        user.lastName.toLowerCase().includes(term) ||
        user.username.toLowerCase().includes(term) ||
        user.email.toLowerCase().includes(term) ||
        this.getRoleName(user.role).toLowerCase().includes(term)
      );
    }
  },
  methods: {
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString('es-ES', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    },
    getInitials(firstName, lastName) {
      return (firstName ? firstName.charAt(0) : '') + (lastName ? lastName.charAt(0) : '');
    },
    getAvatarColor(username) {
      // Simple hash function to generate a consistent color based on username
      let hash = 0;
      for (let i = 0; i < username.length; i++) {
        hash = username.charCodeAt(i) + ((hash << 5) - hash);
      }
      
      const hue = hash % 360;
      return `hsl(${hue}, 70%, 80%)`;
    },
    getRoleName(role) {
      const roles = {
        'ADMIN': 'Administrador',
        'MANAGER': 'Gestor',
        'STAFF': 'Staff',
        'VIEWER': 'Visualizador'
      };
      return roles[role] || role;
    }
  }
};
</script>

<style scoped>
.users-view {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  color: #512da8;
  margin-bottom: 10px;
}

.actions-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 20px 0;
}

.search-box input {
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 300px;
  font-size: 1rem;
}

.btn {
  padding: 10px 15px;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  border: none;
  display: flex;
  align-items: center;
  gap: 5px;
}

.btn-primary {
  background-color: #512da8;
  color: white;
}

.table-container {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
}

.users-table th {
  text-align: left;
  padding: 15px;
  background-color: #f5f5f5;
  color: #333;
  font-weight: 600;
}

.users-table td {
  padding: 15px;
  border-top: 1px solid #eee;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #333;
  font-weight: 500;
  font-size: 0.8rem;
}

.user-name {
  font-weight: 500;
  color: #333;
}

.user-username {
  font-size: 0.85rem;
  color: #666;
}

.role-badge {
  display: inline-block;
  padding: 5px 10px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
}

.role-admin {
  background-color: #fce8e6;
  color: #e74c3c;
}

.role-manager {
  background-color: #e3f2fd;
  color: #0984e3;
}

.role-staff {
  background-color: #e3fcef;
  color: #00b894;
}

.role-viewer {
  background-color: #f1f2f6;
  color: #636e72;
}

.status-badge {
  display: inline-block;
  padding: 5px 10px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
}

.status-active {
  background-color: #e3fcef;
  color: #00b894;
}

.status-inactive {
  background-color: #f1f2f6;
  color: #636e72;
}

.actions-cell {
  display: flex;
  gap: 5px;
}

.btn-icon {
  width: 36px;
  height: 36px;
  border-radius: 4px;
  border: none;
  background-color: #f5f5f5;
  color: #333;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-icon:hover {
  background-color: #e0e0e0;
}

.btn-icon.delete {
  color: #e74c3c;
}

.btn-icon.delete:hover {
  background-color: #fce8e6;
}

.btn-icon.restore {
  color: #28a745;
}

.btn-icon.restore:hover {
  background-color: #e3fcef;
}

@media (max-width: 768px) {
  .actions-bar {
    flex-direction: column;
    align-items: stretch;
    gap: 15px;
  }
  
  .search-box input {
    width: 100%;
  }
  
  .users-table {
    display: block;
    overflow-x: auto;
  }
}
</style> 