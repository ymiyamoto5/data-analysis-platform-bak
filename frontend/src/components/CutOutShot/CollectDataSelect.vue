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
import { formatJST } from '@/common/common'

const DATA_COLLECT_HISTORY_API_URL = '/api/v1/data_collect_histories/'

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
    fetchCollectData: async function(machineId) {
      const client = createBaseApiClient()
      let history = []
      await client
        .get(DATA_COLLECT_HISTORY_API_URL + machineId)
        .then((res) => {
          if (res.data.length === 0) {
            return
          }
          // 日付文字列を表示用にフォーマット
          history = res.data.map((obj) => {
            obj.started_at = formatJST(obj.started_at)

            if (obj.ended_at !== null) {
              obj.ended_at = formatJST(obj.ended_at)
            }
            return obj
          })

          this.items = history.map((x) => x.started_at + ' - ' + x.ended_at)
        })
        .catch((e) => {
          console.log(e.response.data.detail)
          this.errorDialog(e.response.data.detail)
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
