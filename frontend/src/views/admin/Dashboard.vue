<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h1>Dashboard Analítico</h1>
      <p>Centro Cultural Banreservas - Análisis de Datos</p>
      
      <div class="filter-section">
        <label>Filtrar por fechas:</label>
        <input 
          type="date" 
          v-model="startDate" 
          :max="endDate"
          class="date-input"
        />
        <span class="date-separator">hasta</span>
        <input 
          type="date" 
          v-model="endDate" 
          :min="startDate"
          :max="today"
          class="date-input"
        />
        <button @click="applyFilters" class="apply-button">Aplicar Filtros</button>
      </div>
    </div>
    
    <!-- Sección de estadísticas rápidas -->
    <div class="stats-section">
      <h2>Resumen General</h2>
      <div class="stats-cards">
        <div class="stat-card">
          <div class="stat-icon events-icon">
            <i class="fas fa-calendar-alt"></i>
          </div>
          <div class="stat-info">
            <h3>Eventos Totales</h3>
            <p class="stat-value">{{ eventStats.total || 0 }}</p>
            <p class="stat-change">
              <span class="active">{{ eventStats.active || 0 }} activos</span>
            </p>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon visitors-icon">
            <i class="fas fa-users"></i>
          </div>
          <div class="stat-info">
            <h3>Visitantes Totales</h3>
            <p class="stat-value">{{ visitorStats.total || 0 }}</p>
            <p class="stat-change">
              <span class="today">+{{ visitorStats.today || 0 }} hoy</span>
            </p>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon checkin-icon">
            <i class="fas fa-user-check"></i>
          </div>
          <div class="stat-info">
            <h3>Check-ins Hoy</h3>
            <p class="stat-value">{{ visitorStats.checkedIn || 0 }}</p>
            <p class="stat-change">
              <span class="percentage">{{ checkInPercentage }}% del total</span>
            </p>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon peak-icon">
            <i class="fas fa-clock"></i>
          </div>
          <div class="stat-info">
            <h3>Hora Pico</h3>
            <p class="stat-value">{{ peakHour }}</p>
            <p class="stat-change">
              <span class="peak-visitors">{{ peakVisitors }} visitantes</span>
            </p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Gráficos principales -->
    <div class="charts-grid" v-if="!isLoading && !error">
      <div class="chart-wrapper" v-if="chartData.attendanceTrend && chartData.attendanceTrend.length > 0">
        <AttendanceTrend 
          :data="chartData.attendanceTrend"
          height="400px"
        />
      </div>
      
      <div class="chart-wrapper" v-if="chartData.eventTypesComparison && chartData.eventTypesComparison.length > 0">
        <EventTypesComparison 
          :data="chartData.eventTypesComparison"
          height="400px"
        />
      </div>
      
      <div class="chart-wrapper full-width" v-if="chartData.trafficHeatmap && chartData.trafficHeatmap.length > 0">
        <TrafficHeatmap 
          :data="chartData.trafficHeatmap"
          height="400px"
        />
      </div>
      
      <div class="chart-wrapper" v-if="chartData.visitorDistribution && chartData.visitorDistribution.length > 0">
        <VisitorDistribution 
          :data="chartData.visitorDistribution"
          height="400px"
        />
      </div>
      
      <div class="chart-wrapper" v-if="chartData.roomComparison && chartData.roomComparison.length > 0">
        <RoomComparison 
          :data="chartData.roomComparison"
          height="400px"
        />
      </div>
    </div>
    
    <!-- Sección de crecimiento mensual -->
    <div class="monthly-growth-section" v-if="!isLoading && !error && chartData.monthlyGrowth && chartData.monthlyGrowth.length > 0">
      <h2>Crecimiento Mensual</h2>
      <div class="growth-cards">
        <div 
          v-for="month in chartData.monthlyGrowth" 
          :key="month.month"
          class="growth-card"
        >
          <h4>{{ month.month }}</h4>
          <p class="visitors-count">{{ month.visitors }} visitantes</p>
          <p 
            class="growth-rate"
            :class="{ positive: month.growthRate > 0, negative: month.growthRate < 0 }"
          >
            <i :class="getGrowthIcon(month.growthRate)"></i>
            {{ Math.abs(month.growthRate) }}%
          </p>
        </div>
      </div>
    </div>
    
    <!-- Loading y Error states -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="spinner"></div>
      <p>Cargando datos analíticos...</p>
    </div>
    
    <div v-if="error" class="error-message">
      <i class="fas fa-exclamation-triangle"></i>
      <p>{{ error }}</p>
      <button @click="loadDashboardData" class="retry-button">Reintentar</button>
    </div>
  </div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex';
import axios from 'axios';
import AttendanceTrend from '@/components/charts/AttendanceTrend.vue';
import EventTypesComparison from '@/components/charts/EventTypesComparison.vue';
import TrafficHeatmap from '@/components/charts/TrafficHeatmap.vue';
import VisitorDistribution from '@/components/charts/VisitorDistribution.vue';
import RoomComparison from '@/components/charts/RoomComparison.vue';

export default {
  name: 'Dashboard',
  components: {
    AttendanceTrend,
    EventTypesComparison,
    TrafficHeatmap,
    VisitorDistribution,
    RoomComparison
  },
  data() {
    return {
      isLoading: false,
      error: null,
      chartData: {
        attendanceTrend: [],
        eventTypesComparison: [],
        trafficHeatmap: [],
        visitorDistribution: [],
        roomComparison: [],
        peakHours: [],
        monthlyGrowth: []
      },
      startDate: '',
      endDate: '',
      today: new Date().toISOString().split('T')[0]
    };
  },
  computed: {
    ...mapGetters({
      eventStats: 'events/statistics',
      visitorStats: 'visitors/statistics'
    }),
    
    checkInPercentage() {
      if (!this.visitorStats.total || this.visitorStats.total === 0) return 0;
      return Math.round((this.visitorStats.checkedIn / this.visitorStats.total) * 100);
    },
    
    peakHour() {
      if (!this.chartData.peakHours || this.chartData.peakHours.length === 0) {
        return '--:--';
      }
      return this.chartData.peakHours[0].hour;
    },
    
    peakVisitors() {
      if (!this.chartData.peakHours || this.chartData.peakHours.length === 0) {
        return 0;
      }
      return this.chartData.peakHours[0].count;
    }
  },
  created() {
    // Establecer fechas por defecto (último mes)
    const end = new Date();
    const start = new Date();
    start.setMonth(start.getMonth() - 1);
    
    this.endDate = end.toISOString().split('T')[0];
    this.startDate = start.toISOString().split('T')[0];
  },
  async mounted() {
    await this.loadDashboardData();
  },
  methods: {
    ...mapActions({
      fetchEventStats: 'events/fetchStatistics',
      fetchVisitorStats: 'visitors/fetchStatistics'
    }),
    
    async loadDashboardData() {
      this.isLoading = true;
      this.error = null;
      
      try {
        // Cargar estadísticas básicas con manejo de errores
        const statsPromises = [
          this.fetchEventStats().catch(err => {
            console.error('Error cargando estadísticas de eventos:', err);
            return null;
          }),
          this.fetchVisitorStats().catch(err => {
            console.error('Error cargando estadísticas de visitantes:', err);
            return null;
          })
        ];
        
        await Promise.all(statsPromises);
        
        // Cargar datos analíticos avanzados
        try {
          const response = await axios.get('/api/dashboard-data', {
            params: {
              startDate: this.startDate,
              endDate: this.endDate
            }
          });
          
          if (response.data && response.data.success) {
            this.chartData = response.data.data || {};
            console.log('Datos del dashboard cargados:', this.chartData);
          } else {
            throw new Error('Respuesta inválida del servidor');
          }
        } catch (axiosError) {
          console.error('Error cargando datos analíticos:', axiosError);
          // Usar datos de ejemplo si la API falla
          this.loadSampleData();
        }
        
      } catch (error) {
        console.error('Error en dashboard:', error);
        this.error = error.response?.data?.error || 'Error al cargar los datos analíticos';
      } finally {
        this.isLoading = false;
      }
    },
    
    loadSampleData() {
      // Cargar datos de ejemplo para desarrollo
      this.chartData = {
        attendanceTrend: [
          { date: '2025-05-01', visitors: 45 },
          { date: '2025-05-02', visitors: 52 },
          { date: '2025-05-03', visitors: 48 },
          { date: '2025-05-04', visitors: 67 },
          { date: '2025-05-05', visitors: 55 }
        ],
        eventTypesComparison: [
          { type: 'Charlas', totalVisitors: 320, eventsCount: 8, avgAttendance: 40 },
          { type: 'Exposiciones', totalVisitors: 450, eventsCount: 5, avgAttendance: 90 },
          { type: 'Teatro', totalVisitors: 280, eventsCount: 4, avgAttendance: 70 },
          { type: 'Música', totalVisitors: 380, eventsCount: 6, avgAttendance: 63 }
        ],
        trafficHeatmap: [],
        visitorDistribution: [
          { range: '18-25', count: 120, percentage: 15 },
          { range: '26-35', count: 224, percentage: 28 },
          { range: '36-45', count: 200, percentage: 25 },
          { range: '46-55', count: 144, percentage: 18 },
          { range: '56-65', count: 80, percentage: 10 },
          { range: '65+', count: 32, percentage: 4 }
        ],
        roomComparison: [
          { room: 'Sala Principal', eventCount: 12, totalVisitors: 480, avgAttendance: 40 },
          { room: 'Sala de Conferencias', eventCount: 8, totalVisitors: 240, avgAttendance: 30 },
          { room: 'Galería', eventCount: 5, totalVisitors: 150, avgAttendance: 30 }
        ],
        peakHours: [
          { hour: '18:00', count: 95 },
          { hour: '19:00', count: 87 },
          { hour: '17:00', count: 76 }
        ],
        monthlyGrowth: [
          { month: 'Enero 2025', visitors: 420, growthRate: 0 },
          { month: 'Febrero 2025', visitors: 465, growthRate: 10.7 },
          { month: 'Marzo 2025', visitors: 510, growthRate: 9.7 },
          { month: 'Abril 2025', visitors: 495, growthRate: -2.9 },
          { month: 'Mayo 2025', visitors: 540, growthRate: 9.1 }
        ]
      };
      
      console.log('Datos de ejemplo cargados');
    },
    
    async applyFilters() {
      await this.loadDashboardData();
    },
    
    getGrowthIcon(rate) {
      if (rate > 0) return 'fas fa-arrow-up';
      if (rate < 0) return 'fas fa-arrow-down';
      return 'fas fa-minus';
    }
  }
};
</script>

<style scoped>
.dashboard {
  width: 100%;
  padding: 20px;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.dashboard-header {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 30px;
  margin-bottom: 30px;
}

.dashboard-header h1 {
  color: #474C55;
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 10px 0;
}

.dashboard-header p {
  color: #666;
  font-size: 16px;
  margin: 0 0 20px 0;
}

.filter-section {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-top: 20px;
}

.filter-section label {
  color: #666;
  font-weight: 500;
}

.date-input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  outline: none;
  transition: all 0.3s;
}

.date-input:focus {
  border-color: #00BDF2;
}

.date-separator {
  color: #999;
  font-size: 14px;
}

.apply-button {
  background-color: #F99D2A;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.apply-button:hover {
  background-color: #E68A1A;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* Sección de estadísticas */
.stats-section {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 25px;
  margin-bottom: 30px;
}

.stats-section h2 {
  color: #474C55;
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 20px 0;
}

.stats-cards {
  display: grid;
  gap: 20px;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
}

.stat-card {
  align-items: center;
  background-color: #f8f9fa;
  border-radius: 12px;
  display: flex;
  padding: 20px;
  transition: all 0.3s;
}

.stat-card:hover {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.stat-icon {
  align-items: center;
  border-radius: 16px;
  display: flex;
  font-size: 24px;
  height: 64px;
  justify-content: center;
  margin-right: 20px;
  width: 64px;
}

.events-icon {
  background-color: rgba(249, 157, 42, 0.15);
  color: #F99D2A;
}

.visitors-icon {
  background-color: rgba(0, 189, 242, 0.15);
  color: #00BDF2;
}

.checkin-icon {
  background-color: rgba(40, 167, 69, 0.15);
  color: #28A745;
}

.peak-icon {
  background-color: rgba(71, 76, 85, 0.15);
  color: #474C55;
}

.stat-info h3 {
  color: #666;
  font-size: 14px;
  font-weight: 500;
  margin: 0 0 8px 0;
}

.stat-value {
  color: #333;
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 4px 0;
}

.stat-change {
  color: #999;
  font-size: 13px;
  margin: 0;
}

.stat-change span {
  font-weight: 600;
}

.stat-change .active {
  color: #F99D2A;
}

.stat-change .today {
  color: #28A745;
}

.stat-change .percentage {
  color: #00BDF2;
}

.stat-change .peak-visitors {
  color: #474C55;
}

/* Grid de gráficos */
.charts-grid {
  display: grid;
  gap: 30px;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  margin-bottom: 30px;
}

.chart-wrapper {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 20px;
  transition: all 0.3s;
}

.chart-wrapper:hover {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.chart-wrapper.full-width {
  grid-column: span 2;
}

/* Sección de crecimiento mensual */
.monthly-growth-section {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 25px;
  margin-bottom: 30px;
}

.monthly-growth-section h2 {
  color: #474C55;
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 20px 0;
}

.growth-cards {
  display: grid;
  gap: 20px;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
}

.growth-card {
  background-color: #f8f9fa;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  transition: all 0.3s;
}

.growth-card:hover {
  background-color: #f0f0f0;
  transform: translateY(-2px);
}

.growth-card h4 {
  color: #666;
  font-size: 14px;
  font-weight: 500;
  margin: 0 0 10px 0;
}

.visitors-count {
  color: #333;
  font-size: 20px;
  font-weight: 700;
  margin: 0 0 10px 0;
}

.growth-rate {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
}

.growth-rate.positive {
  color: #28A745;
}

.growth-rate.negative {
  color: #DC3545;
}

/* Loading overlay */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.spinner {
  animation: spin 1s linear infinite;
  border: 4px solid #f3f3f3;
  border-radius: 50%;
  border-top: 4px solid #F99D2A;
  height: 50px;
  margin-bottom: 20px;
  width: 50px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-overlay p {
  color: #666;
  font-size: 16px;
  font-weight: 500;
}

/* Error message */
.error-message {
  background-color: #FEE;
  border: 1px solid #FCC;
  border-radius: 8px;
  color: #C33;
  margin: 20px 0;
  padding: 20px;
  text-align: center;
}

.error-message i {
  font-size: 32px;
  margin-bottom: 10px;
}

.error-message p {
  font-size: 16px;
  margin: 10px 0;
}

.retry-button {
  background-color: #DC3545;
  border: none;
  border-radius: 6px;
  color: white;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  margin-top: 10px;
  padding: 8px 20px;
  transition: all 0.3s;
}

.retry-button:hover {
  background-color: #C82333;
  transform: translateY(-1px);
}

/* Responsive design */
@media (max-width: 1200px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .chart-wrapper.full-width {
    grid-column: span 1;
  }
}

@media (max-width: 768px) {
  .dashboard {
    padding: 10px;
  }
  
  .dashboard-header {
    padding: 20px;
  }
  
  .dashboard-header h1 {
    font-size: 24px;
  }
  
  .filter-section {
    flex-direction: column;
    align-items: stretch;
  }
  
  .stats-cards {
    grid-template-columns: 1fr;
  }
  
  .growth-cards {
    grid-template-columns: 1fr;
  }
  
  .chart-wrapper {
    padding: 15px;
  }
  
  .monthly-growth-section {
    padding: 15px;
  }
}
</style>
