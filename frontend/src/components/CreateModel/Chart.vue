<script>
import { Line } from 'vue-chartjs'
export default {
  extends: Line,
  name: 'Chart',
  props: ['chartData', 'options'],
  watch: {
    chartData: function() {
      this.renderChart(this.chartData, this.options)
    },
  },
  mounted() {
    this.renderChart(this.chartData, this.options)
  },
}
</script>
