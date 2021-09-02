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
      let data = []
      await client
        .get(DATA_COLLECT_HISTORY_API_URL)
        .then((res) => {
          if (res.data.length === 0) {
            return
          }
          data = res.data
          console.log(data)
          // 日付文字列を表示用にフォーマット
          this.history = data.map((obj) => {
            const started_at = new Date(obj.started_at)
            obj.started_at = this.formatDate(started_at)

            if (obj.ended_at !== null) {
              const ended_at = new Date(obj.ended_at)
              obj.ended_at = this.formatDate(ended_at)
            }
            return obj
          })
        })
        .catch((e) => {
          console.log(e.response.data.message)
        })
    },
    // Date型を表示用にフォーマットして返す
    formatDate: function(x) {
      const formatted =
        x.getFullYear() +
        '/' +
        ('00' + (x.getMonth() + 1)).slice(-2) +
        '/' +
        ('00' + x.getDate()).slice(-2) +
        ' ' +
        ('00' + x.getHours()).slice(-2) +
        ':' +
        ('00' + x.getMinutes()).slice(-2) +
        ':' +
        ('00' + x.getSeconds()).slice(-2)
      return formatted
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
