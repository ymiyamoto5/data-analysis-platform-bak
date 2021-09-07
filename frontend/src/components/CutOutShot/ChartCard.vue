<template>
  <v-card min-width="80%">
    <v-card-text class="chart-container">
      <Chart v-if="loaded" :chartData="chartData" :options="options" />
      <!-- <v-progress-circular
        v-else-if="loaded != true"
        indeterminate
        color="#53e09c"
      /> -->
    </v-card-text>
  </v-card>
</template>

<script>
import { createBaseApiClient } from '@/api/apiBase'
import { formatTime } from '@/common/common'
import Chart from './Chart.vue'

const SHOTS_API_URL = '/api/v1/shots'

export default {
  props: ['machineId', 'collectData'],
  components: {
    Chart,
  },
  watch: {
    machineId: function() {
      this.chartData.datasets.data = []
    },
    collectData: function(new_value) {
      this.chartData.datasets.data = []
      this.fetchData(new_value)
    },
  },
  data() {
    return {
      loaded: false,
      chartData: {
        labels: null,
        datasets: [
          {
            label: '変位データ',
            data: null,
            fill: false,
            backgroundColor: 'rgba(232, 229, 74, 0.2)',
            borderColor: '#e8e54a',
          },
        ],
      },
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
    fetchData: async function(collectData) {
      // ex) 2021/09/06 14:59:38 - 2021/09/06 15:00:00 => 2021/09/06 14:59:38 => UNIXTIME(ミリ秒)
      const targetDate = Date.parse(collectData.split('-')[0].slice(0, -1))

      const client = createBaseApiClient()
      await client
        .get(SHOTS_API_URL, {
          params: {
            machineId: this.machineId,
            targetDate: targetDate,
          },
        })
        .then((res) => {
          if (res.data.length === 0) {
            return
          }
          // x軸データ
          let x_data = res.data.map((x) => new Date(x.timestamp))
          x_data = x_data.map((x) => formatTime(x))
          this.$set(this.chartData, 'labels', x_data)
          // y軸データ
          const displacement_data = res.data.map((x) => x.displacement)
          this.$set(this.chartData.datasets[0], 'data', displacement_data)

          this.loaded = true
        })
        .catch((e) => {
          console.log(e.response.data.message)
        })
    },
  },
}
</script>
