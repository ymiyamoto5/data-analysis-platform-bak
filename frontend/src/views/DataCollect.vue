<template>
  <app>
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
            <v-card
              :key="gateway.gateway_id"
              class="pa-1 text-center"
              min-width="50%"
              max-width="100%"
            >
              {{ gateway.gateway_id }}
            </v-card>
          </template>
        </template>

        <template v-slot:[`item.handlers`]="{ item }">
          <template v-for="gateway in item.gateways">
            <template v-for="handler in gateway.handlers">
              <v-card
                :key="handler.hanlder_id"
                class="pa-1 text-center"
                min-width="50%"
                max-width="100%"
              >
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
                  <v-card
                    :key="sensor.sensor_name"
                    class="pa-1 text-center"
                    min-width="50%"
                    max-width="100%"
                  >
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
          <v-btn
            disabled
            v-if="item.collect_status === 'error'"
            color="disable"
          >
            ゲートウェイエラー
          </v-btn>
          <v-btn disabled v-if="item.collect_status === ''" color="disable">
            状態不明
          </v-btn>
        </template>
      </v-data-table>
    </v-card>

    <v-snackbar v-model="snackbar" timeout="5000" top color="success">
      {{ snackbarMessage }}
      <template v-slot:action="{ attrs }">
        <v-btn color="white" text v-bind="attrs" @click="snackbar = false">
          Close
        </v-btn>
      </template>
    </v-snackbar>
  </app>
</template>

<script>
import { createBaseApiClient } from '@/api/apiBase'

const MACHINES_API_URL = '/api/v1/machines/'
const CONTROLLER_API_URL = '/api/v1/controller/'
const SETUP_API_URL = CONTROLLER_API_URL + 'setup/'
const START_API_URL = CONTROLLER_API_URL + 'start/'
const STOP_API_URL = CONTROLLER_API_URL + 'stop/'
const CHECK_API_URL = CONTROLLER_API_URL + 'check/'
const PAUSE_API_URL = CONTROLLER_API_URL + 'pause/'
const RESUME_API_URL = CONTROLLER_API_URL + 'resume/'

export default {
  name: 'data-collect',
  data() {
    return {
      headers: [
        {
          text: '機器ID',
          align: 'start',
          value: 'machine_id',
          width: '10%',
        },
        { text: '機器名', value: 'machine_name', width: '15%' },
        { text: '機種', value: 'machine_type.machine_type_name', width: '15%' },
        {
          text: 'ゲートウェイID',
          value: 'gateways',
          sortable: false,
          width: '15%',
        },
        {
          text: 'ハンドラーID',
          value: 'handlers',
          sortable: false,
          width: '15%',
        },
        { text: 'センサー', value: 'sensors', sortable: false, width: '20%' },
        { text: 'アクション', value: 'actions', sortable: false, width: '20%' },
      ],
      machines: [],
      collectStatus: '',
      search: '',
      snackbar: false,
      snackbarMessage: '',
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
      await client
        .get(MACHINES_API_URL)
        .then((res) => {
          if (res.data.length === 0) {
            return
          }
          this.machines = res.data
        })
        .catch((e) => {
          console.log(e.response.data.detail)
          this.errorDialog(e.response.data.detail)
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
          console.log(e.response.data.detail)
          this.errorDialog(e.response.data.detail)
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
          console.log(e.response.data.detail)
          this.errorDialog(e.response.data.detail)
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
          console.log(e.response.data.detail)
          this.errorDialog(e.response.data.detail)
        })
    },
    check: async function(machine_id) {
      const client = createBaseApiClient()
      await client
        .post(CHECK_API_URL + machine_id)
        .then(() => {
          this.fetchTableData()
          this.snackbarMessage = machine_id + 'のデータ収集が完了しました'
          this.snackbar = true
        })
        .catch((e) => {
          console.log(e.response.data.detail)
          this.errorDialog(e.response.data.detail)
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
          console.log(e.response.data.detail)
          this.errorDialog(e.response.data.detail)
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
          console.log(e.response.data.detail)
          this.errorDialog(e.response.data.detail)
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

.v-card {
  margin-top: 1%;
  margin-bottom: 1%;
}

ul {
  list-style: none;
}
</style>
