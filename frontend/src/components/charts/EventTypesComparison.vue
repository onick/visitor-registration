<template>
  <div :id="chartId" class="chart-container" :style="{ height: height }"></div>
</template>

<script>
import * as echarts from 'echarts';

export default {
  name: 'EventTypesComparison',
  props: {
    chartId: {
      type: String,
      default: 'event-types-comparison'
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
          text: 'Comparativa por Tipo de Evento',
          left: 'center',
          textStyle: {
            fontSize: 18,
            fontWeight: 'bold',
            color: '#474C55'
          }
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          },
          formatter: (params) => {
            if (!params[0]) return '';
            const type = params[0].axisValue;
            const total = params[0].value || 0;
            const eventData = this.data.find(d => d.type === type);
            const events = eventData?.eventsCount || 0;
            const avg = eventData?.avgAttendance || 0;
            return `${type}<br>
                    Total visitantes: ${total}<br>
                    Eventos: ${events}<br>
                    Promedio: ${avg} por evento`;
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
          data: this.data.map(item => item.type),
          axisLabel: {
            color: '#666',
            interval: 0,
            rotate: 30
          }
        },
        yAxis: {
          type: 'value',
          name: 'Total de Visitantes',
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
          data: this.data.map(item => item.totalVisitors || 0),
          type: 'bar',
          barWidth: '60%',
          itemStyle: {
            color: '#F99D2A',
            borderRadius: [8, 8, 0, 0]
          },
          emphasis: {
            itemStyle: {
              color: '#E68A1A'
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
