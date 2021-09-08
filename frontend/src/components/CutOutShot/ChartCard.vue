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
  props: [
    'machineId',
    'targetDir',
    'startDisplacement',
    'endDisplacement',
    'page',
  ],
  components: {
    Chart,
  },
  watch: {
    machineId: function() {},
    targetDir: function() {
      this.loaded = false
      this.fetchData()
    },
    startDisplacement: function() {
      this.createChartData(this.responseData)
    },
    endDisplacement: function() {
      this.createChartData(this.responseData)
    },
    page: function() {
      this.loaded = false
      this.fetchData()
    },
  },
  data() {
    return {
      display: false,
      loaded: false,
      responseData: [], // グラフデータ
      maxPage: 0,
      chartDataTemplate: {
        labels: null,
        datasets: [
          {
            label: '変位値',
            data: null,
            fill: false,
            borderColor: '#000080',
            borderWidth: 1,
            pointRadius: 0,
          },
          {
            label: '切り出し開始',
            data: null,
            fill: false,
            borderColor: '#008000',
            borderWidth: 1,
            pointRadius: 0,
          },
          {
            label: '切り出し終了',
            data: null,
            fill: false,
            borderColor: '#ff0000',
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
        animation: {
          duration: 0,
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
            machine_id: this.machineId,
            targetDir: this.targetDir,
            page: this.page,
          },
        })
        .then((res) => {
          if (res.data.length === 0) {
            return
          }
          this.responseData = res.data.data
          this.maxPage = res.data.fileCount
          this.$emit('setMaxPage', this.maxPage)
          this.createChartData(this.responseData)
          this.loaded = true
        })
        .catch((e) => {
          console.log(e.response.data.message)
        })
    },
    createChartData: function(data) {
      // x軸データ
      let xData = data.map((x) => new Date(x.timestamp))
      xData = xData.map((x) => formatTime(x))
      // y軸データ
      let displacementData = data.map((x) => x.displacement)
      // NOTE: chartをリアクティブにするためchartDataオブジェクトをディープコピー
      // https://qiita.com/nicopinpin/items/17457d38444b08953049
      let chartData = JSON.parse(JSON.stringify(this.chartDataTemplate))
      this.$set(chartData, 'labels', xData)
      this.$set(chartData.datasets[0], 'data', displacementData)

      if (this.startDisplacement !== 0) {
        let startData = []
        for (let i = 0; i < displacementData.length; i++) {
          startData.push(this.startDisplacement)
        }
        this.$set(chartData.datasets[1], 'data', startData)
      }
      if (this.endDisplacement !== 0) {
        let endData = []
        for (let i = 0; i < displacementData.length; i++) {
          endData.push(this.endDisplacement)
        }
        this.$set(chartData.datasets[2], 'data', endData)
      }

      this.chartData = chartData
    },
  },
}
</script>
