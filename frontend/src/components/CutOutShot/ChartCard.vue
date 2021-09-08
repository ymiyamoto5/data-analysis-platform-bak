<template>
  <v-card min-width="80%" v-if="display">
    <v-card-text class="chart-container">
      <Chart v-if="loaded" :chartData="chartData" :options="options" />
      <v-progress-circular
        v-else-if="loaded != true"
        indeterminate
        color="#53e09c"
      />
    </v-card-text>
  </v-card>
</template>

<script>
import { createBaseApiClient } from '@/api/apiBase'
import { formatTime } from '@/common/common'
import Chart from './Chart.vue'

const SHOTS_API_URL = '/api/v1/shots'

export default {
  props: ['machine_id', 'targetDir'],
  components: {
    Chart,
  },
  watch: {
    machine_id: function() {},
    targetDir: function() {
      this.loaded = false
      this.fetchData()
    },
  },
  data() {
    return {
      display: false,
      loaded: false,
      chartDataTemplate: {
        labels: null,
        datasets: [
          {
            label: '変位値',
            data: null,
            fill: false,
            backgroundColor: 'rgba(232, 229, 74, 0.2)',
            borderColor: '#000080',
            borderWidth: 1,
            pointRadius: 0,
          },
        ],
      },
      chartData: null,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        legend: {
          display: true,
        },
      },
    }
  },
  methods: {
    fetchData: async function() {
      this.display = true

      const client = createBaseApiClient()
      await client
        .get(SHOTS_API_URL, {
          params: {
            machine_id: this.machine_id,
            targetDir: this.targetDir,
          },
        })
        .then((res) => {
          if (res.data.length === 0) {
            return
          }
          // x軸データ
          let x_data = res.data.map((x) => new Date(x.timestamp))
          x_data = x_data.map((x) => formatTime(x))
          // y軸データ
          let displacement_data = res.data.map((x) => x.displacement)
          // NOTE: chartをリアクティブにするためchartDataオブジェクトをディープコピー
          // https://qiita.com/nicopinpin/items/17457d38444b08953049
          let chartData = JSON.parse(JSON.stringify(this.chartDataTemplate))
          this.$set(chartData, 'labels', x_data)
          this.$set(chartData.datasets[0], 'data', displacement_data)
          this.chartData = chartData

          this.loaded = true
        })
        .catch((e) => {
          console.log(e.response.data.message)
        })
    },
  },
}
</script>
