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
import Chart from './Chart.vue'

const FEATURE_API_URL = '/api/v1/features/'

export default {
  props: ['machineId', 'targetDir', 'feature'],
  components: {
    Chart,
  },
  watch: {
    machineId: function() {},
    targetDir: function() {
      this.loaded = false
      this.fetchData()
    },
    feature: function(new_feature) {
      this.createChartData(new_feature)
    },
  },
  data() {
    return {
      display: false,
      loaded: false,
      responseData: [], // グラフデータ
      featureNames: [],
      chartDataTemplate: {
        labels: null,
        datasets: [
          {
            label: '',
            data: null,
            fill: false,
            borderColor: '#000080',
            borderWidth: 1,
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
          ],
          xAxes: [
            {
              ticks: {
                callback: (value) => (value % 5 == 0 ? value : ''),
              },
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
        .get(FEATURE_API_URL, {
          params: {
            machine_id: this.machineId,
            target_dir: this.targetDir,
          },
        })
        .then((res) => {
          if (res.data.length === 0) {
            return
          }
          this.responseData = res.data.data
          this.featureNames = Object.keys(this.responseData)
          this.$emit('setFeatures', this.featureNames)
          this.createChartData(this.featureNames[0])
          this.loaded = true
        })
        .catch((e) => {
          console.log(e.response.data.detail)
        })
    },
    createChartData: function(featureName) {
      const data = this.responseData[featureName]
      const xData = [...data.keys()]

      // NOTE: chartをリアクティブにするためchartDataオブジェクトをディープコピー
      // https://qiita.com/nicopinpin/items/17457d38444b08953049
      let chartData = JSON.parse(JSON.stringify(this.chartDataTemplate))
      this.$set(chartData, 'labels', xData)
      this.$set(chartData.datasets[0], 'label', featureName)
      this.$set(chartData.datasets[0], 'data', data)

      this.chartData = chartData
    },
  },
}
</script>
