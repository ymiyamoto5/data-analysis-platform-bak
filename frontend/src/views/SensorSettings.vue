<template>
  <v-data-table
    :headers="headers"
    :items="sensors"
    multi-sort
    :sort-by="['machine_id', 'sensor_id']"
    class="elevation-1"
  >
    <template v-slot:top>
      <v-toolbar flat>
        <v-toolbar-title>センサー管理</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-dialog v-model="dialog" max-width="500px">
          <template v-slot:activator="{ on, attrs }">
            <v-btn color="primary" dark class="mb-2" v-bind="attrs" v-on="on">
              新規作成
            </v-btn>
          </template>
          <v-card>
            <v-card-title>
              <span class="text-h5">{{ formTitle }}</span>
            </v-card-title>

            <v-card-text>
              <v-form ref="form_group">
                <v-text-field
                  v-model="editedItem.sensor_name"
                  :rules="[rules.required, rules.counter]"
                  label="センサー名"
                ></v-text-field>
                <v-select
                  v-model="editedItem.sensor_type_id"
                  :rules="[rules.required]"
                  item-text="sensor_type_name"
                  item-value="sensor_type_id"
                  :items="sensorTypes"
                  label="センサー種別"
                  v-bind="readOnlyID"
                >
                </v-select>
                <v-text-field
                  v-model="editedItem.slope"
                  :rules="[rules.floatType]"
                  label="校正（傾き）"
                ></v-text-field>
                <v-text-field
                  v-model="editedItem.intercept"
                  :rules="[rules.floatType]"
                  label="校正（切片）"
                ></v-text-field>
                <v-select
                  v-model="editedItem.handler_id"
                  :rules="[rules.required]"
                  item-text="handler_id"
                  item-value="id"
                  :items="handlers"
                  label="ハンドラーID"
                  v-bind="readOnlyID"
                >
                </v-select>
              </v-form>
            </v-card-text>

            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn color="blue darken-1" text @click="close">
                キャンセル
              </v-btn>
              <v-btn color="blue darken-1" text @click="save">
                保存
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
        <v-dialog v-model="dialogDelete" max-width="500px">
          <v-card>
            <v-card-title class="text-h6">
              機器ID：{{ editedItem.machine_id }}/センサーID：{{
                editedItem.sensor_id
              }}
              を削除してもよいですか？
            </v-card-title>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn color="blue darken-1" text @click="closeDelete"
                >キャンセル</v-btn
              >
              <v-btn color="blue darken-1" text @click="deleteItemConfirm"
                >OK</v-btn
              >
              <v-spacer></v-spacer>
            </v-card-actions>
          </v-card>
        </v-dialog>
      </v-toolbar>
    </template>
    <template v-slot:[`item.actions`]="{ item }">
      <v-icon small class="mr-2" @click="editItem(item)">
        mdi-pencil
      </v-icon>
      <v-icon small @click="deleteItem(item)">
        mdi-delete
      </v-icon>
    </template>
  </v-data-table>
</template>

<script>
import { createBaseApiClient } from '@/api/apiBase'
const SENSORS_API_URL = '/api/v1/sensors/'
const SENSOR_TYPES_API_URL = '/api/v1/sensor_types/'
const HANDLERS_API_URL = '/api/v1/handlers/'

export default {
  data: () => ({
    dialog: false,
    dialogDelete: false,
    headers: [
      {
        text: '機器ID',
        align: 'start',
        value: 'machine_id',
        width: '15%',
      },
      { text: 'センサーID', value: 'sensor_id', width: '15%' },
      { text: 'センサー名', value: 'sensor_name', width: '15%' },
      {
        text: 'センサー種別',
        value: 'sensor_type.sensor_type_name',
        width: '10%',
      },
      { text: '校正（傾き）', value: 'slope', width: '8%' },
      { text: '校正（切片）', value: 'intercept', width: '8%' },
      { text: 'ハンドラーID', value: 'handler_id', width: '13%' },
      { text: 'アクション', value: 'actions', sortable: false, width: '8%' },
    ],
    sensors: [],
    editedIndex: -1,
    editedItem: {
      sensor_name: '',
      sensor_type_id: '',
      slope: null,
      intercept: null,
      handler_id: 0,
    },
    defaultItem: {
      sensor_name: '',
      sensor_type_id: '',
      slope: null,
      intercept: null,
      handler_id: 0,
    },
    handlers: [],
    sensorTypes: [],
    // validation
    rules: {
      required: (value) => !!value || '必須です。',
      counter: (value) => value.length <= 255 || '最大255文字です。',
      idPattern: (value) => {
        const pattern = /^[0-9a-zA-Z-]+$/
        return (
          pattern.test(value) ||
          '半角のアルファベット/数字/ハイフンのみ使用可能です。'
        )
      },
      floatType: (value) =>
        (value >= 0.0 && value <= 100.0) || '0.0～100.0のみ使用可能です。',
    },
  }),

  computed: {
    formTitle() {
      return this.editedIndex === -1 ? '新規作成' : '編集'
    },
    readOnlyID() {
      return this.editedIndex === -1 ? { disabled: false } : { disabled: true }
    },
  },

  // dialogをwatchし、val（bool値）に応じてクローズ
  watch: {
    dialog(val) {
      val || this.close()
    },
    dialogDelete(val) {
      val || this.closeDelete()
    },
  },

  created() {
    this.fetchTableData()
    this.fetchHandlerId()
    this.fetchSensorTypes()
  },

  methods: {
    errorDialog(message) {
      this.$store.commit('setShowErrorDialog', true)
      this.$store.commit('setErrorMsg', message)
    },

    // ドロップダウンリスト用データ取得
    fetchHandlerId: async function() {
      const client = createBaseApiClient()
      await client
        .get(HANDLERS_API_URL)
        .then((res) => {
          if (res.data.length === 0) {
            return
          }
          this.handlers = res.data
        })
        .catch((e) => {
          console.log(e.response.data.detail)
          this.errorDialog(e.response.data.detail)
        })
    },

    fetchSensorTypes: async function() {
      const client = createBaseApiClient()
      await client
        .get(SENSOR_TYPES_API_URL)
        .then((res) => {
          if (res.data.length === 0) {
            return
          }
          this.sensorTypes = res.data
        })
        .catch((e) => {
          console.log(e.response.data.detail)
          this.errorDialog(e.response.data.detail)
        })
    },

    fetchTableData: async function() {
      const client = createBaseApiClient()
      await client
        .get(SENSORS_API_URL)
        .then((res) => {
          if (res.data.length === 0) {
            this.sensors = []
          }
          this.sensors = res.data
        })
        .catch((e) => {
          console.log(e.response.data.detail)
          this.errorDialog(e.response.data.detail)
        })
    },

    // 新規作成 or 編集ダイアログ表示。itemはテーブルで選択したレコードのオブジェクト。
    editItem(item) {
      this.editedIndex = this.sensors.indexOf(item)
      this.editedItem = Object.assign({}, item)
      this.dialog = true
    },

    // [保存] 押下時の処理（update or insert）
    save: async function() {
      // form_groupと名付けたv-formを参照し、検証してエラーがあれば何もしない。
      if (!this.$refs.form_group.validate()) {
        return
      }
      let url = ''
      let body = {}
      const client = createBaseApiClient()

      // 空文字の時nullに置き換え
      const slope = this.editedItem.slope === '' ? null : this.editedItem.slope
      const intercept =
        this.editedItem.intercept === '' ? null : this.editedItem.intercept

      // update
      if (this.editedIndex > -1) {
        url = SENSORS_API_URL + this.editedItem.sensor_id + '/'
        body = {
          machine_id: this.editedItem.machine_id,
          sensor_name: this.editedItem.sensor_name,
          sensor_type_id: this.editedItem.sensor_type_id,
          slope: slope,
          intercept: intercept,
          handler_id: this.editedItem.handler_id,
        }
        await client
          .put(url, body)
          .then(() => {
            this.dialog = false
            this.fetchTableData()
          })
          .catch((e) => {
            console.log(e.response.data.detail)
            this.errorDialog(e.response.data.detail)
          })
      }
      // insert
      else {
        url = SENSORS_API_URL
        body = {
          sensor_name: this.editedItem.sensor_name,
          sensor_type_id: this.editedItem.sensor_type_id,
          slope: slope,
          intercept: intercept,
          handler_id: this.editedItem.handler_id,
        }
        await client
          .post(url, body)
          .then(() => {
            this.dialog = false
            this.fetchTableData()
          })
          .catch((e) => {
            console.log(e.response.data.detail)
            this.errorDialog(e.response.data.detail)
          })
      }
    },

    // 新規作成 or 編集ダイアログclose
    close() {
      this.dialog = false
      // HACK: https://qiita.com/funkj/items/f19bdab0f0430e45323d
      setTimeout(() => {
        this.editedItem = Object.assign({}, this.defaultItem)
        this.editedIndex = -1
        this.$refs.form_group.resetValidation()
      }, 500)
    },

    // 削除ダイアログ表示
    deleteItem(item) {
      this.editedIndex = this.sensors.indexOf(item)
      this.editedItem = Object.assign({}, item)
      this.dialogDelete = true
    },

    // 削除
    deleteItemConfirm: async function() {
      let url = ''
      let body = {}
      url = SENSORS_API_URL + this.editedItem.sensor_id + '/'
      body = {
        machine_id: this.editedItem.machine_id,
      }

      const client = createBaseApiClient()
      // HACK: https://teratail.com/questions/296013
      await client
        .request({
          method: 'delete',
          url: url,
          data: body,
        })
        .then(() => {
          this.dialogDelete = false
          this.fetchTableData()
        })
        .catch((e) => {
          console.log(e.response.data.detail)
          this.errorDialog(e.response.data.detail)
        })
    },

    // 削除ダイアログclose
    closeDelete() {
      this.dialogDelete = false
      setTimeout(() => {
        this.editedItem = Object.assign({}, this.defaultItem)
        this.editedIndex = -1
        if (this.$refs.form_group) {
          this.$refs.form_group.resetValidation()
        }
      })
    },
  },
}
</script>
