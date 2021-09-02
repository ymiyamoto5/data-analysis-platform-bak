<template>
  <v-data-table
    :headers="headers"
    :items="gateways"
    sort-by="gateway_id"
    class="elevation-1"
  >
    <template v-slot:top>
      <v-toolbar flat>
        <v-toolbar-title>ゲートウェイ管理</v-toolbar-title>
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
                  v-model="editedItem.gateway_id"
                  :rules="[rules.required, rules.counter, rules.idPattern]"
                  label="ゲートウェイID"
                  v-bind="readOnlyID"
                ></v-text-field>
                <v-text-field
                  v-model="editedItem.log_level"
                  :rules="[rules.required, rules.counter, rules.logLevelPattern]"
                  label="ログレベル"
                ></v-text-field>
                <v-select
                  v-model="editedItem.machine_id"
                  :rules="[rules.required]"
                  item-text="machine_id"
                  item-value="id"
                  :items="machines"
                  label="機器ID"
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
              ゲートウェイID：{{ editedItem.gateway_id }} を削除してもよいですか？
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
const GATEWAYS_API_URL = '/api/v1/gateways'
const MACHINES_API_URL = '/api/v1/machines'

export default {
  data: () => ({
    dialog: false,
    dialogDelete: false,
    headers: [
      {
        text: 'ゲートウェイID',
        align: 'start',
        value: 'gateway_id',
      },
      { text: '操作連番', value: 'sequence_number' },
      { text: '設定状態', value: 'gateway_result' },
      { text: '動作状態', value: 'status' },
      { text: 'ログレベル', value: 'log_level'} ,
      { text: '機器ID', value: 'machines[0].machine_id' },
      { text: 'アクション', value: 'actions', sortable: false }
    ],
    gateways: [],
    editedIndex: -1,
    editedItem: {
      gateway_id: '',
      log_level: '',
      machine_id: 0,
    },
    defaultItem: {
      gateway_id: '',
      sequence_number: '',
      gateway_result: '',
      status: '',
      log_level: '',
      machine_id: 0,
    },
    machines: [],
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
      logLevelPattern: (value) => {
        const pattern = /^[0-9]+$/
        return (
          pattern.test(value) ||
          '半角の数字のみ使用可能です。'
        )
      },
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
    this.fetchMachineId()
  },

  methods: {
    errorDialog(message) {
      this.$store.commit('setShowErrorDialog', true)
      this.$store.commit('setErrorMsg', message)
    },

    // ドロップダウンリスト用データ取得
    fetchMachineId: async function() {
      const client = createBaseApiClient()
      let data = []
      await client
        .get(MACHINES_API_URL)
        .then((res) => {
          if (res.data.length === 0) {
            return
          }
          data = res.data
          this.machines = data
        })
        .catch((e) => {
          console.log(e.response.data.message)
          this.errorDialog(e.response.data.message)
        })
    },

    fetchTableData: async function() {
      const client = createBaseApiClient()
      let data = []
      await client
        .get(GATEWAYS_API_URL)
        .then((res) => {
          if (res.data.length === 0) {
            return
          }
          data = res.data
          this.gateways = data
        })
        .catch((e) => {
          console.log(e.response.data.message)
          this.errorDialog(e.response.data.message)
        })
    },

    // 新規作成 or 編集ダイアログ表示。itemはテーブルで選択したレコードのオブジェクト。
    editItem(item) {
      this.editedIndex = this.gateways.indexOf(item)
      this.editedItem = Object.assign({}, item)
      this.dialog = true
    },

    // [保存] 押下時の処理（update or insert）
    save: async function() {
      // form_groupと名付けたv-formを参照し、検証してエラーがあれば何もしない。
      if (!this.$refs.form_group.validate()) {
        return
      }
      let postUrl = ''
      let postData = {}
      // update
      if (this.editedIndex > -1) {
        postUrl =
          GATEWAYS_API_URL + '/' + this.editedItem.gateway_id + '/update'
        postData = {
          log_level: this.editedItem.log_level,
          machine_id: this.editedItem.machine_id,
        }
      }
      // insert
      else {
        postUrl = GATEWAYS_API_URL
        postData = {
          gateway_id: this.editedItem.gateway_id,
          log_level: this.editedItem.log_level,
          machine_id: this.editedItem.machine_id,
        }
      }

      const client = createBaseApiClient()
      await client
        .post(postUrl, postData)
        .then(() => {
          // this.close()
          this.dialog = false
          this.fetchTableData()
        })
        .catch((e) => {
          console.log(e.response.data.message)
          this.errorDialog(e.response.data.message)
        })
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
      this.editedIndex = this.gateways.indexOf(item)
      this.editedItem = Object.assign({}, item)
      this.dialogDelete = true
    },

    // 削除
    deleteItemConfirm: async function() {
      const postUrl =
        GATEWAYS_API_URL + '/' + this.editedItem.gateway_id + '/delete'

      const client = createBaseApiClient()
      await client
        .post(postUrl)
        .then(() => {
          this.dialogDelete = false
          this.fetchTableData()
        })
        .catch((e) => {
          console.log(e.response.data.message)
          this.errorDialog(e.response.data.message)
        })
    },

    // 削除ダイアログclose
    closeDelete() {
      this.dialogDelete = false
      setTimeout(() => {
        this.editedItem = Object.assign({}, this.defaultItem)
        this.editedIndex = -1
        this.$refs.form_group.resetValidation()
      })
    },
  },
}
</script>
