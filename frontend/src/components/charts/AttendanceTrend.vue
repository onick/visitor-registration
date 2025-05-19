<template>
  <div :id="chartId" class="chart-container" :style="{ height: height }"></div>
</template>

<script>
import * as echarts from 'echarts';

export default {
  name: 'AttendanceTrend',
  props: {
    chartId: {
      type: String,
      default: 'attendance-trend'
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
      if (!this.chart || !this.data) return;
      
      const option = {
        title: {
          text: 'Tendencia de Asistencia',
          left: 'center',
          textStyle: {
            fontSize: 18,
            fontWeight: 'bold',
            color: '#474C55'
          }
        },
        tooltip: {
          trigger: 'axis',
          formatter: (params) => {
            if (!params[0]) return '';
            const date = params[0].axisValue;
            const value = params[0].value || 0;
            return `${date}<br>Visitantes: ${value}`;
          }
        },
        grid: {
          left: '5%',
          right: '5%',
          bottom: '10%',
          top: '15%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: this.data.map(item => {
            const date = new Date(item.date);
            return date.toLocaleDateString('es-ES', { 
              day: 'numeric', 
              month: 'short' 
            });
          }),
          axisLabel: {
            rotate: 45,
            color: '#666'
          },
          axisTick: {
            alignWithLabel: true
          }
        },
        yAxis: {
          type: 'value',
          name: 'Visitantes',
          axisLabel: {
            color: '#666'
          },
          splitLine: {
            lineStyle: {
              color: '#eee'
            }
          }
        },
        series: [{
          data: this.data.map(item => item.visitors || 0),
          type: 'line',
          smooth: true,
          symbol: 'circle',
          symbolSize: 8,
          lineStyle: {
            color: '#00BDF2',
            width: 3
          },
          itemStyle: {
            color: '#00BDF2',
            borderColor: '#fff',
            borderWidth: 2
          },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: 'rgba(0, 189, 242, 0.3)' },
                { offset: 1, color: 'rgba(0, 189, 242, 0.05)' }
              ]
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
