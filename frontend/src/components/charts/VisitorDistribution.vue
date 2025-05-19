<template>
  <div :id="chartId" class="chart-container" :style="{ height: height }"></div>
</template>

<script>
import * as echarts from 'echarts';

export default {
  name: 'VisitorDistribution',
  props: {
    chartId: {
      type: String,
      default: 'visitor-distribution'
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
      if (!this.chart) return;
      
      const option = {
        title: {
          text: 'Distribución de Visitantes por Edad',
          left: 'center',
          textStyle: {
            fontSize: 18,
            fontWeight: 'bold',
            color: '#474C55'
          }
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b} : {c} ({d}%)'
        },
        legend: {
          bottom: '5%',
          left: 'center',
          data: this.data.map(item => item.range),
          textStyle: {
            color: '#666'
          }
        },
        series: [{
          name: 'Rango de Edad',
          type: 'pie',
          radius: ['40%', '70%'],
          center: ['50%', '50%'],
          data: this.data.map(item => ({
            value: item.count,
            name: item.range,
            itemStyle: {
              color: this.getColorForRange(item.range)
            }
          })),
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          },
          label: {
            show: true,
            formatter: '{b}\n{d}%',
            position: 'outside',
            textStyle: {
              color: '#666'
            }
          },
          labelLine: {
            show: true,
            length: 15,
            length2: 10
          }
        }]
      };
      
      this.chart.setOption(option);
    },
    getColorForRange(range) {
      const colors = {
        '18-25': '#00BDF2',
        '26-35': '#F99D2A',
        '36-45': '#474C55',
        '46-55': '#5CB3CC',
        '56-65': '#E68A1A',
        '65+': '#A3D9E9'
      };
      return colors[range] || '#999999';
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
