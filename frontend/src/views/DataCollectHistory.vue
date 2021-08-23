<template>
  <div id="history">
    <div id="title">
      <h1>データ収集履歴</h1>
    </div>
    <div id="history-table">
      <v-card>
        <v-card-title>
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
    </div>
  </div>
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
          this.history = data
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