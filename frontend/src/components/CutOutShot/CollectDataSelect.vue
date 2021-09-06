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
import { formatDate } from '@/common/common'

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
      let history = []
      await client
        .get(DATA_COLLECT_HISTORY_API_URL + '/' + machine_id)
        .then((res) => {
          if (res.data.length === 0) {
            return
          }
          // 日付文字列を表示用にフォーマット
          history = res.data.map((obj) => {
            const started_at = new Date(obj.started_at)
            obj.started_at = formatDate(started_at)

            if (obj.ended_at !== null) {
              const ended_at = new Date(obj.ended_at)
              obj.ended_at = formatDate(ended_at)
            }
            return obj
          })

          this.items = history.map((x) => x.started_at + ' - ' + x.ended_at)
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
  width: 430px;
}
</style>
