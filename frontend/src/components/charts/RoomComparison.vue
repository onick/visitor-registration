<template>
  <div :id="chartId" class="chart-container" :style="{ height: height }"></div>
</template>

<script>
import * as echarts from 'echarts';

export default {
  name: 'RoomComparison',
  props: {
    chartId: {
      type: String,
      default: 'room-comparison'
    },
    height: {
      type: String,
      default: '400px'
    },
    data: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      chart: null
    };
  },
  mounted() {
    this.initChart();
    window.addEventListener('resize', this.handleResize);
  },
  beforeUnmount() {
    if (this.chart) {
      this.chart.dispose();
    }
    window.removeEventListener('resize', this.handleResize);
  },
  watch: {
    data: {
      deep: true,
      handler() {
        this.updateChart();
      }
    }
  },
  methods: {
    initChart() {
      const chartDom = document.getElementById(this.chartId);
      this.chart = echarts.init(chartDom);
      this.updateChart();
    },
    updateChart() {
      if (!this.chart || !this.data || this.data.length === 0) return;
      
      const maxVisitors = Math.max(...this.data.map(d => d.totalVisitors || 0));
      const maxEvents = Math.max(...this.data.map(d => d.eventCount || 0));
      const maxAvg = Math.max(...this.data.map(d => d.avgAttendance || 0));
      
      const indicators = [
        { name: 'Total Visitantes', max: maxVisitors * 1.2 || 100 },
        { name: 'Eventos', max: maxEvents * 1.2 || 10 },
        { name: 'Promedio por Evento', max: maxAvg * 1.2 || 50 }
      ];
      
      const option = {
        title: {
          text: 'Comparación de Asistencia entre Salas',
          left: 'center',
          textStyle: {
            fontSize: 18,
            fontWeight: 'bold',
            color: '#474C55'
          }
        },
        tooltip: {
          trigger: 'item',
          formatter: (params) => {
            const room = params.name;
            const roomData = this.data.find(d => d.room === room);
            if (!roomData) return '';
            return `${room}<br>
                    Total Visitantes: ${roomData.totalVisitors}<br>
                    Eventos: ${roomData.eventCount}<br>
                    Promedio: ${roomData.avgAttendance}`;
          }
        },
        legend: {
          data: this.data.map(item => item.room),
          bottom: '5%',
          left: 'center',
          textStyle: {
            color: '#666'
          }
        },
        radar: {
          shape: 'polygon',
          indicator: indicators,
          name: {
            textStyle: {
              color: '#666'
            }
          },
          splitArea: {
            areaStyle: {
              color: ['rgba(0, 189, 242, 0.1)', 'rgba(249, 157, 42, 0.1)']
            }
          }
        },
        series: [{
          name: 'Salas',
          type: 'radar',
          data: this.data.map((item, index) => ({
            name: item.room,
            value: [
              item.totalVisitors || 0, 
              item.eventCount || 0, 
              item.avgAttendance || 0
            ],
            itemStyle: {
              color: this.getColorForIndex(index)
            },
            lineStyle: {
              color: this.getColorForIndex(index),
              width: 2
            },
            areaStyle: {
              color: this.getTransparentColor(index)
            }
          }))
        }]
      };
      
      this.chart.setOption(option);
    },
    getColorForIndex(index) {
      const colors = ['#00BDF2', '#F99D2A', '#474C55', '#5CB3CC', '#E68A1A'];
      return colors[index % colors.length];
    },
    getTransparentColor(index) {
      const colors = [
        'rgba(0, 189, 242, 0.3)',
        'rgba(249, 157, 42, 0.3)',
        'rgba(71, 76, 85, 0.3)',
        'rgba(92, 179, 204, 0.3)',
        'rgba(230, 138, 26, 0.3)'
      ];
      return colors[index % colors.length];
    },
    handleResize() {
      if (this.chart) {
        this.chart.resize();
      }
    }
  }
};
</script>

<style scoped>
.chart-container {
  width: 100%;
  min-height: 300px;
}
</style>
