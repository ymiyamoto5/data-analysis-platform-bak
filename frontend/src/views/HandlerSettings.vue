<template>
  <v-data-table
    :headers="headers"
    :items="handlers"
    sort-by="handler_id"
    class="elevation-1"
  >
    <template v-slot:top>
      <v-toolbar flat>
        <v-toolbar-title>ハンドラー管理</v-toolbar-title>
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
                  v-model="editedItem.handler_id"
                  :rules="[rules.required, rules.counter, rules.idPattern]"
                  label="ハンドラーID"
                  v-bind="readOnlyID"
                ></v-text-field>
                <v-select
                  v-model="editedItem.handler_type"
                  :rules="[rules.required]"
                  :items="handlerTypes"
                  label="ハンドラータイプ"
                >
                </v-select>
                <v-text-field
                  v-model="editedItem.adc_serial_num"
                  :rules="[rules.required, rules.counter, rules.idPattern]"
                  label="シリアルナンバー"
                ></v-text-field>
                <v-text-field
                  v-model="editedItem.sampling_frequency"
                  :rules="[rules.required, rules.frequencyRange]"
                  label="サンプリングレート(Hz)"
                ></v-text-field>
                <v-text-field
                  v-model="editedItem.filewrite_time"
                  :rules="[rules.required, rules.filewriteTimeRange]"
                  label="ファイル出力間隔(秒)"
                ></v-text-field>
                <v-select
                  v-model="editedItem.gateway_id"
                  :rules="[rules.required]"
                  item-text="gateway_id"
                  item-value="id"
                  :items="gateways"
                  label="ゲートウェイID"
                  v-bind="readOnlyID"
                  @input="checkPrimary"
                >
                </v-select>
                <v-checkbox
                  v-model="editedItem.is_cut_out_target"
                  hide-details
                  label="ショット切り出し対象"
                >
                </v-checkbox>
                <v-checkbox
                  v-model="editedItem.is_primary"
                  hide-details
                  label="主要なハンドラー"
                  :disabled="
                    editedItem.gateway_id === '' ||
                      (primary !== '' && editedItem.handler_id !== primary)
                  "
                >
                  <template v-slot:append>
                    <v-tooltip bottom>
                      <template v-slot:activator="{ on }">
                        <v-icon v-on="on">
                          mdi-help-circle-outline
                        </v-icon>
                      </template>
                      <div>
                        複数ハンドラー構成時の主要なハンドラーに設定します。これはゲートウェイごとに1つのハンドラーのみ設定可能です。
                      </div>
                    </v-tooltip>
                  </template>
                </v-checkbox>
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
              ハンドラーID：{{ editedItem.handler_id }} を削除してもよいですか？
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
    <template v-slot:[`item.is_primary`]="{ item }">
      {{ formatBool(item.is_primary) }}
    </template>
    <template v-slot:[`item.actions`]="{ item }">
      <v-icon
        small
        class="mr-2"
        @click="
          editItem(item)
          checkPrimary()
        "
      >
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
const GATEWAYS_API_URL = '/api/v1/gateways/'
const HANDLERS_API_URL = '/api/v1/handlers/'
const PRIMARY_HANDLER_API_URL = '/api/v1/handlers/primary/'

export default {
  data: () => ({
    dialog: false,
    dialogDelete: false,
    headers: [
      {
        text: 'ハンドラーID',
        align: 'start',
        value: 'handler_id',
      },
      { text: 'ハンドラータイプ', value: 'handler_type' },
      { text: 'シリアルナンバー', value: 'adc_serial_num' },
      { text: 'サンプリングレート(Hz)', value: 'sampling_frequency' },
      { text: 'チャンネル数', value: 'sampling_ch_num' },
      { text: 'ファイル出力間隔(秒)', value: 'filewrite_time' },
      { text: 'ゲートウェイID', value: 'gateway_id' },
      { text: 'ショット切り出し対象', value: 'is_cut_out_target' },
      { text: '主要なハンドラー', value: 'is_primary' },
      { text: 'アクション', value: 'actions', sortable: false },
    ],
    handlers: [],
    editedIndex: -1,
    editedItem: {
      handler_id: '',
      handler_type: '',
      adc_serial_num: '',
      sampling_frequency: '',
      sampling_ch_num: '',
      filewrite_time: '',
      gateway_id: '',
      is_cut_out_target: false,
      is_primary: false,
    },
    defaultItem: {
      handler_id: '',
      handler_type: '',
      adc_serial_num: '',
      sampling_frequency: '',
      sampling_ch_num: '',
      filewrite_time: '',
      is_cut_out_target: false,
      gateway_id: '',
      is_primary: false,
    },
    primary: '',
    gateways: [],
    handlerTypes: ['USB_204', 'USB_1608HS'],
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
      frequencyRange: (value) =>
        (value >= 1 && value <= 100000) || '1~100,000のみ使用可能です。',
      filewriteTimeRange: (value) =>
        (value >= 1 && value <= 360) || '1~360のみ使用可能です。',
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
    this.fetchGatewayId()
  },

  methods: {
    errorSnackbar(message) {
      this.$store.commit('setShowErrorSnackbar', true)
      this.$store.commit('setErrorHeader', message.statusText)
      this.$store.commit('setErrorMsg', message.data.detail)
    },

    // ドロップダウンリスト用データ取得
    fetchGatewayId: async function() {
      const client = createBaseApiClient()
      await client
        .get(GATEWAYS_API_URL)
        .then((res) => {
          if (res.data.length === 0) {
            return
          }
          this.gateways = res.data
        })
        .catch((e) => {
          console.log(e.response.data.detail)
          this.errorSnackbar(e.response)
        })
    },

    fetchTableData: async function() {
      const client = createBaseApiClient()
      await client
        .get(HANDLERS_API_URL)
        .then((res) => {
          if (res.data.length === 0) {
            this.handlers = []
            return
          }
          this.handlers = res.data
        })
        .catch((e) => {
          console.log(e.response.data.detail)
          this.errorSnackbar(e.response)
        })
    },

    // 主要なハンドラーのbool値を表示用にフォーマット
    formatBool(bool) {
      return bool ? 'YES' : 'NO'
    },

    // 主要なハンドラーが設定されているかを確認
    checkPrimary: async function() {
      const client = createBaseApiClient()
      await client
        .get(PRIMARY_HANDLER_API_URL + this.editedItem.gateway_id)
        .then((res) => {
          if (res.data === null) {
            this.primary = ''
            return
          }
          this.primary = res.data.handler_id
        })
        .catch((e) => {
          console.log(e.response.data.detail)
          this.errorSnackbar(e.response)
        })
    },

    // 新規作成 or 編集ダイアログ表示。itemはテーブルで選択したレコードのオブジェクト。
    editItem(item) {
      this.editedIndex = this.handlers.indexOf(item)
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

      // update
      if (this.editedIndex > -1) {
        url = HANDLERS_API_URL + this.editedItem.handler_id
        body = {
          handler_type: this.editedItem.handler_type,
          adc_serial_num: this.editedItem.adc_serial_num,
          sampling_ch_num: this.editedItem.sampling_ch_num,
          filewrite_time: this.editedItem.filewrite_time,
          is_cut_out_target: this.editedItem.is_cut_out_target,
          is_primary: this.editedItem.is_primary,
        }
        await client
          .put(url, body)
          .then(() => {
            this.dialog = false
            this.fetchTableData()
          })
          .catch((e) => {
            console.log(e.response.data.detail)
            this.errorSnackbar(e.response)
          })
      }
      // insert
      else {
        url = HANDLERS_API_URL
        body = {
          handler_id: this.editedItem.handler_id,
          handler_type: this.editedItem.handler_type,
          adc_serial_num: this.editedItem.adc_serial_num,
          sampling_frequency: this.editedItem.sampling_frequency,
          filewrite_time: this.editedItem.filewrite_time,
          gateway_id: this.editedItem.gateway_id,
          is_cut_out_target: this.editedItem.is_cut_out_target,
          is_primary: this.editedItem.is_primary,
        }
        await client
          .post(url, body)
          .then(() => {
            this.dialog = false
            this.fetchTableData()
          })
          .catch((e) => {
            console.log(e.response.data.detail)
            this.errorSnackbar(e.response)
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
      this.editedIndex = this.handlers.indexOf(item)
      this.editedItem = Object.assign({}, item)
      this.dialogDelete = true
    },

    // 削除
    deleteItemConfirm: async function() {
      const url = HANDLERS_API_URL + this.editedItem.handler_id

      const client = createBaseApiClient()
      await client
        .delete(url)
        .then(() => {
          this.dialogDelete = false
          this.fetchTableData()
        })
        .catch((e) => {
          console.log(e.response.data.detail)
          this.errorSnackbar(e.response)
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
