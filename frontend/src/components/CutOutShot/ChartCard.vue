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

const SHOTS_API_URL = '/api/v1/cut_out_shot/shots'

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
            yAxisID: 'y-axis-1',
          },
          {
            label: '荷重',
            data: null,
            fill: false,
            borderColor: '#800080',
            borderWidth: 1,
            pointRadius: 0,
            yAxisID: 'y-axis-2',
          },
          {
            label: '切り出し開始',
            data: null,
            fill: false,
            borderColor: '#008000',
            borderWidth: 2,
            pointRadius: 0,
            yAxisID: 'y-axis-1',
          },
          {
            label: '切り出し終了',
            data: null,
            fill: false,
            borderColor: '#ff0000',
            borderWidth: 2,
            pointRadius: 0,
            yAxisID: 'y-axis-1',
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
        scales: {
          yAxes: [
            {
              id: 'y-axis-1',
              type: 'linear',
              position: 'left',
            },
            {
              id: 'y-axis-2',
              type: 'linear',
              position: 'right',
            },
          ],
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
            target_dir: this.targetDir,
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
          console.log(e.response.data.detail)
        })
    },
    createChartData: function(data) {
      // x軸データ
      // let xData = data.map((x) => new Date(x.timestamp))
      let xData = data.map((x) => formatTime(x.timestamp))
      // y軸データ
      const displacementData = data.map((x) => x.displacement)
      // TODO: 動的に数を決定する
      const load01 = data.map((x) => x.load01)

      // NOTE: chartをリアクティブにするためchartDataオブジェクトをディープコピー
      // https://qiita.com/nicopinpin/items/17457d38444b08953049
      let chartData = JSON.parse(JSON.stringify(this.chartDataTemplate))
      this.$set(chartData, 'labels', xData)
      this.$set(chartData.datasets[0], 'data', displacementData)
      this.$set(chartData.datasets[1], 'data', load01)

      // 切り出し開始位置と終了位置の直線データ
      let startData = []
      for (let i = 0; i < displacementData.length; i++) {
        startData.push(this.startDisplacement)
      }
      this.$set(chartData.datasets[2], 'data', startData)

      let endData = []
      for (let i = 0; i < displacementData.length; i++) {
        endData.push(this.endDisplacement)
      }
      this.$set(chartData.datasets[3], 'data', endData)

      this.chartData = chartData
    },
  },
}
</script>
