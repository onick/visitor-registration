<template>
  <div :id="chartId" class="chart-container" :style="{ height: height }"></div>
</template>

<script>
import * as echarts from 'echarts';

export default {
  name: 'TrafficHeatmap',
  props: {
    chartId: {
      type: String,
      default: 'traffic-heatmap'
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
      chart: null,
      days: ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'],
      hours: Array.from({ length: 24 }, (_, i) => `${i}:00`)
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
      if (!this.chart) return;
      
      const formattedData = this.data.map(item => [
        item.hour,
        item.day,
        item.value || 0
      ]);
      
      const option = {
        title: {
          text: 'Mapa de Calor - Tráfico de Visitantes',
          left: 'center',
          textStyle: {
            fontSize: 18,
            fontWeight: 'bold',
            color: '#474C55'
          }
        },
        tooltip: {
          position: 'top',
          formatter: (params) => {
            const hour = this.hours[params.value[0]];
            const day = this.days[params.value[1]];
            const value = params.value[2];
            return `${day} ${hour}<br>Visitantes: ${value}`;
          }
        },
        animation: false,
        grid: {
          left: '5%',
          right: '5%',
          bottom: '10%',
          top: '15%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: this.hours,
          splitArea: {
            show: true
          },
          axisLabel: {
            color: '#666',
            interval: 1
          }
        },
        yAxis: {
          type: 'category',
          data: this.days,
          splitArea: {
            show: true
          },
          axisLabel: {
            color: '#666'
          }
        },
        visualMap: {
          min: 0,
          max: Math.max(...this.data.map(d => d.value || 0)),
          calculable: true,
          orient: 'horizontal',
          left: 'center',
          bottom: '0%',
          inRange: {
            color: ['#E8F4F8', '#A3D9E9', '#5CB3CC', '#F99D2A', '#E68A1A']
          }
        },
        series: [{
          name: 'Tráfico',
          type: 'heatmap',
          data: formattedData,
          label: {
            show: true,
            formatter: (params) => params.value[2] || 0
          },
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }]
      };
      
      this.chart.setOption(option);
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
