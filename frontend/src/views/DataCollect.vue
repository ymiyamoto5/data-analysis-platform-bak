<template>
  <v-card>
    <v-card-title>
      データ収集
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
      :items="machines"
      :search="search"
      sort-by="machine_id"
    >
      <template v-slot:[`item.gateways`]="{ item }">
        <template v-for="gateway in item.gateways">
          <v-card :key="gateway.gateway_id" class="pa-2 text-center" tile>
            {{ gateway.gateway_id }}
          </v-card>
        </template>
      </template>

      <template v-slot:[`item.handlers`]="{ item }">
        <template v-for="gateway in item.gateways">
          <template v-for="handler in gateway.handlers">
            <v-card :key="handler.hanlder_id" class="pa-2 text-center" tile>
              {{ handler.handler_id }}
            </v-card>
          </template>
        </template>
      </template>

      <template v-slot:[`item.sensors`]="{ item }">
        <v-card
          class="d-flex align-content-start flex-wrap"
          flat
          tile
          max-width="300"
        >
          <template v-for="gateway in item.gateways">
            <template v-for="handler in gateway.handlers">
              <template v-for="sensor in handler.sensors">
                <v-card :key="sensor.sensor_name" class="pa-2" tile>
                  {{ sensor.sensor_name }}
                </v-card>
              </template>
            </template>
          </template>
        </v-card>
      </template>

      <template v-slot:[`item.actions`]="{ item }">
        <v-btn
          v-if="item.collect_status === 'recorded'"
          color="primary"
          @click="setup(item.machine_id)"
        >
          段取開始
        </v-btn>
        <v-btn
          v-if="item.collect_status === 'setup'"
          color="success"
          @click="start(item.machine_id)"
        >
          収集開始
        </v-btn>
        <v-btn
          v-if="item.collect_status === 'start'"
          color="error"
          @click="beforeStop(item.machine_id)"
        >
          停止
        </v-btn>
        <v-btn
          v-if="item.collect_status === 'start'"
          color="warning"
          @click="pause(item.machine_id)"
        >
          中断
        </v-btn>
        <v-btn
          v-if="item.collect_status === 'pause'"
          color="blue"
          class="white--text"
          @click="resume(item.machine_id)"
        >
          再開
        </v-btn>
        <v-btn
          disabled
          v-if="item.collect_status === 'stop'"
          color="grey"
          class="white--text"
        >
          記録中
        </v-btn>
        <v-btn disabled v-if="item.collect_status === 'error'" color="disable">
          ゲートウェイエラー
        </v-btn>
        <v-btn disabled v-if="item.collect_status === ''" color="disable">
          状態不明
        </v-btn>
      </template>
    </v-data-table>
  </v-card>
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
      headers: [
        {
          text: '機器ID',
          align: 'start',
          value: 'machine_id',
        },
        { text: '機器名', value: 'machine_name' },
        { text: '機種', value: 'machine_type.machine_type_name' },
        { text: 'ゲートウェイID', value: 'gateways', sortable: false },
        { text: 'ハンドラーID', value: 'handlers', sortable: false },
        { text: 'センサー', value: 'sensors', sortable: false },
        { text: 'アクション', value: 'actions', sortable: false },
      ],
      machines: [],
      collectStatus: '',
      search: '',
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
          this.errorDialog(e.response.data.message)
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
