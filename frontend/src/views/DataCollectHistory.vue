<template>
  <v-card>
    <v-card-title>
      データ収集履歴
      <v-spacer></v-spacer>
      <v-text-field
        v-model="search"
        append-icon="mdi-magnify"
        label="Search"
        single-line
        hide-details
      ></v-text-field>
    </v-card-title>
    <v-data-table
      :headers="headers"
      :items="history"
      :search="search"
    ></v-data-table>
  </v-card>
</template>

<script>
import { createBaseApiClient } from '@/api/apiBase'
import { formatDate } from '@/common/common'

const DATA_COLLECT_HISTORY_API_URL = '/api/v1/data_collect_history'

export default {
  name: 'data-collect-history',
  data() {
    return {
      headers: [
        {
          text: '機器名',
          align: 'start',
          value: 'machine_name',
        },
        {
          text: '開始日時',
          value: 'started_at',
        },
        {
          text: '終了日時',
          value: 'ended_at',
        },
      ],
      search: '',
      history: [],
    }
  },
  created: function() {
    this.fetchTableData()
  },
  methods: {
    fetchTableData: async function() {
      const client = createBaseApiClient()
      await client
        .get(DATA_COLLECT_HISTORY_API_URL)
        .then((res) => {
          if (res.data.length === 0) {
            return
          }
          // 日付文字列を表示用にフォーマット
          this.history = res.data.map((obj) => {
            const started_at = new Date(obj.started_at)
            obj.started_at = formatDate(started_at)

            if (obj.ended_at !== null) {
              const ended_at = new Date(obj.ended_at)
              obj.ended_at = formatDate(ended_at)
            }
            return obj
          })
        })
        .catch((e) => {
          console.log(e.response.data.message)
        })
    },
  },
}
</script>

<style scoped>
#title {
  margin: 15px;
}
.v-btn {
  margin-right: 10px;
}
ul {
  list-style: none;
}
</style>
