<template>
  <v-select
    class="select"
    :items="items"
    label="収集データ"
    outlined
    dense
    @input="$emit('input', $event)"
  ></v-select>
</template>

<script>
import { createBaseApiClient } from '@/api/apiBase'
const DATA_COLLECT_HISTORY_API_URL = '/api/v1/data_collect_history'

export default {
  props: ['value'],
  data() {
    return {
      items: [],
    }
  },
  watch: {
    value: function(new_value) {
      this.items = []
      this.fetchCollectData(new_value)
    },
  },
  methods: {
    fetchCollectData: async function(machine_id) {
      const client = createBaseApiClient()
      await client
        .get(DATA_COLLECT_HISTORY_API_URL + '/' + machine_id)
        .then((res) => {
          if (res.data.length === 0) {
            return
          }
          this.items = res.data.map((x) => x.started_at + ' - ' + x.ended_at)
        })
        .catch((e) => {
          console.log(e.response.data.message)
          this.errorDialog(e.response.data.message)
        })
    },
  },
}
</script>

<style scoped>
.select {
  width: 200px;
}
</style>
