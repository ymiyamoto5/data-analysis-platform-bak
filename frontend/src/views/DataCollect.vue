<template>
  <div id="machines">
    <div id="title">
      <h1>データ収集</h1>
    </div>
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
                @click="setup(machine.machine_id)"
              >
                段取開始
              </v-btn>
              <v-btn
                v-if="machine.collect_status === 'setup'"
                color="success"
                @click="start(machine.machine_id)"
              >
                収集開始
              </v-btn>
              <v-btn
                v-if="machine.collect_status === 'start'"
                color="error"
                @click="beforeStop(machine.machine_id)"
              >
                停止
              </v-btn>
              <v-btn
                v-if="machine.collect_status === 'start'"
                color="warning"
                @click="pause(machine.machine_id)"
              >
                中断
              </v-btn>
              <v-btn
                v-if="machine.collect_status === 'pause'"
                color="blue"
                class="white--text"
                @click="resume(machine.machine_id)"
              >
                再開
              </v-btn>
              <v-btn
                disabled
                v-if="machine.collect_status === 'stop'"
                color="grey"
                class="white--text"
              >
                記録中
              </v-btn>
              <v-btn
                disabled
                v-if="machine.collect_status === 'error'"
                color="disable"
              >
                ゲートウェイエラー
              </v-btn>
              <v-btn
                disabled
                v-if="machine.collect_status === ''"
                color="disable"
              >
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
const CONTROLLER_API_URL = '/api/v1/controller'
const SETUP_API_URL = CONTROLLER_API_URL + '/setup/'
const START_API_URL = CONTROLLER_API_URL + '/start/'
const STOP_API_URL = CONTROLLER_API_URL + '/stop/'
const CHECK_API_URL = CONTROLLER_API_URL + '/check/'
const PAUSE_API_URL = CONTROLLER_API_URL + '/pause/'
const RESUME_API_URL = CONTROLLER_API_URL + '/resume/'

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
    confirmDialog(message, callback, param) {
      this.$store.commit('setShowConfirmDialog', true)
      this.$store.commit('setConfirmMsg', message)
      this.$store.commit('setCallbackFunc', callback)
      this.$store.commit('setCallbackFuncParam', param)
    },
    errorDialog(message) {
      this.$store.commit('setShowErrorDialog', true)
      this.$store.commit('setErrorMsg', message)
    },
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
        .catch((e) => {
          console.log(e.response.data.message)
          this.confirm_dialog(e.response.data.message)
        })
    },
    setup: async function(machine_id) {
      const client = createBaseApiClient()
      await client
        .post(SETUP_API_URL + machine_id)
        .then(() => {
          this.fetchTableData()
        })
        .catch((e) => {
          console.log(e.response.data.message)
          this.errorDialog(e.response.data.message)
        })
    },
    start: async function(machine_id) {
      const client = createBaseApiClient()
      await client
        .post(START_API_URL + machine_id)
        .then(() => {
          this.fetchTableData()
        })
        .catch((e) => {
          console.log(e.response.data.message)
          this.errorDialog(e.response.data.message)
        })
    },
    beforeStop(machine_id) {
      this.confirmDialog('停止してもよいですか？', this.stop, machine_id)
    },
    stop: async function(machine_id) {
      const client = createBaseApiClient()
      await client
        .post(STOP_API_URL + machine_id)
        .then(() => {
          this.fetchTableData()
          // データファイルがなくなるまで待ち
          this.check(machine_id)
        })
        .catch((e) => {
          console.log(e.response.data.message)
          this.errorDialog(e.response.data.message)
        })
    },
    check: async function(machine_id) {
      const client = createBaseApiClient()
      await client
        .post(CHECK_API_URL + machine_id)
        .then(() => {
          this.fetchTableData()
        })
        .catch((e) => {
          console.log(e.response.data.message)
          this.errorDialog(e.response.data.message)
        })
    },
    pause: async function(machine_id) {
      const client = createBaseApiClient()
      await client
        .post(PAUSE_API_URL + machine_id)
        .then(() => {
          this.fetchTableData()
        })
        .catch((e) => {
          console.log(e.response.data.message)
          this.errorDialog(e.response.data.message)
        })
    },
    resume: async function(machine_id) {
      const client = createBaseApiClient()
      await client
        .post(RESUME_API_URL + machine_id)
        .then(() => {
          this.fetchTableData()
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
