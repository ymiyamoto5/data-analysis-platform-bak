<template>
  <div id="machines">
    <v-simple-table>
      <thead>
        <tr>
          <th v-for="item in Object.keys(tableHeader)" :key="item">
            {{ tableHeader[item] }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="machine in machines" :key="machine.machine_id">
          <td>{{ machine.machine_name }}</td>
          <td>
            <ul>
              <li v-for="gateway in machine.gateways" :key="gateway.gateway_id">
                {{ gateway.gateway_id }}
              </li>
            </ul>
          </td>
          <td>
            <ul>
              <template v-for="gateway in machine.gateways">
                <li
                  v-for="handler in gateway.handlers"
                  :key="handler.handler_id"
                >
                  {{ handler.handler_id }}
                </li>
              </template>
            </ul>
          </td>
          <td>
            <ul>
              <template v-for="gateway in machine.gateways">
                <template v-for="handler in gateway.handlers">
                  <li v-for="sensor in handler.sensors" :key="sensor.sensor_id">
                    {{ sensor.sensor_name }}
                  </li>
                </template>
              </template>
            </ul>
          </td>
          <td>
            <ul>
              <v-btn
                v-if="machine.collect_status === 'recorded'"
                color="primary"
                @click="setup()"
              >
                段取開始
              </v-btn>
              <v-btn v-if="machine.collect_status === 'setup'" color="success">
                収集開始
              </v-btn>
              <v-btn v-if="machine.collect_status === 'start'" color="error">
                停止
              </v-btn>
              <v-btn v-if="machine.collect_status === 'start'" color="warning">
                中断
              </v-btn>
              <v-btn
                v-if="machine.collect_status === 'pause'"
                color="blue"
                class="white--text"
              >
                再開
              </v-btn>
              <v-btn
                v-if="machine.collect_status === 'stop'"
                color="grey"
                class="white--text"
              >
                記録中
              </v-btn>
              <v-btn v-if="machine.collect_status === 'error'" color="disable">
                ゲートウェイエラー
              </v-btn>
              <v-btn v-if="machine.collect_status === ''" color="disable">
                状態不明
              </v-btn>
            </ul>
          </td>
        </tr>
      </tbody>
    </v-simple-table>
  </div>
</template>

<script>
import { createBaseApiClient } from '@/api/apiBase'

const MACHINES_API_URL = '/api/v1/machines'
const DATA_COLLECT_API_URL = '/api/v1/data_collect'
const SETUP_API_URL = DATA_COLLECT_API_URL + '/setup'

export default {
  name: 'data-collect',
  data() {
    return {
      tableHeader: {
        machine_name: '機器',
        gateway_id: 'ゲートウェイID',
        handler_id: 'ハンドラーID',
        sensor_name: 'センサー',
        status: 'アクション',
      },
      machines: [],
      collectStatus: '',
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
        .get(MACHINES_API_URL)
        .then((res) => {
          if (res.data.length === 0) {
            return
          }
          data = res.data
          console.log(data)
          this.machines = data
        })
        .catch(() => {
          console.log('error')
        })
    },
    setup: async function() {
      const client = createBaseApiClient()
      await client
        .post(SETUP_API_URL)
        .then((res) => {
          if (res.data.length === 0) {
            return
          }
          this.fetchTableData()
        })
        .catch(() => {
          console.log('error')
        })
    },
  },
}
</script>

<style scoped>
.v-btn {
  margin-right: 10px;
}
ul {
  list-style: none;
}
</style>
