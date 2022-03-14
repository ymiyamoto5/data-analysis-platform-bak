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

    <v-data-table :headers="headers" :items="history" :search="search">
      <template v-slot:top>
        <v-dialog v-model="dialog" max-width="1980px">
          <v-card>
            <v-card-title>
              <span class="text-h5">編集</span>
            </v-card-title>

            <v-card-text>
              <v-form ref="form_group">
                <div
                  v-for="(gateway,
                  key) in editedItem.data_collect_history_gateways"
                  :key="key"
                  class="text-h5"
                >
                  {{ gateway.gateway_id }}
                  <div
                    v-for="(handler, _key) in editedItem
                      .data_collect_history_gateways[key]
                      .data_collect_history_handlers"
                    :key="_key"
                  >
                    {{ handler.handler_id }}

                    <v-text-field
                      v-model="
                        editedItem.data_collect_history_gateways[key]
                          .data_collect_history_handlers[_key]
                          .sampling_frequency
                      "
                      :rules="[rules.required, rules.frequencyRange]"
                      label="サンプリングレート"
                    ></v-text-field>

                    <v-data-table
                      :headers="detailHeaders"
                      :items="
                        editedItem.data_collect_history_gateways[key]
                          .data_collect_history_handlers[_key]
                          .data_collect_history_sensors
                      "
                    >
                      <template v-slot:[`item.slope`]="props">
                        <v-text-field
                          v-model="props.item.slope"
                          :rules="[rules.required, rules.floatType]"
                        ></v-text-field>
                      </template>
                      <template v-slot:[`item.intercept`]="props">
                        <v-text-field
                          v-model="props.item.intercept"
                          :rules="[rules.required, rules.floatType]"
                        ></v-text-field>
                      </template>
                      <template v-slot:[`item.start_point_dsl`]="props">
                        <v-text-field
                          v-model="props.item.start_point_dsl"
                        ></v-text-field>
                      </template>
                      <template v-slot:[`item.max_point_dsl`]="props">
                        <v-text-field
                          v-model="props.item.max_point_dsl"
                        ></v-text-field>
                      </template>
                      <template v-slot:[`item.break_point_dsl`]="props">
                        <v-text-field
                          v-model="props.item.break_point_dsl"
                        ></v-text-field>
                      </template>
                    </v-data-table>
                  </div>
                </div>
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
              この履歴を削除すると、収集したデータも削除されます。削除してもよいですか？
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
  </v-card>
</template>

<script>
import { createBaseApiClient } from '@/api/apiBase'
import { formatJST } from '@/common/common'

const DATA_COLLECT_HISTORY_API_URL = '/api/v1/data_collect_histories/'

export default {
  name: 'data-collect-history',
  data() {
    return {
      dialog: false,
      dialogDelete: false,
      editedIndex: -1,
      editedItem: {
        id: -1,
        machine_id: '',
        machine_name: '',
        machine_type_id: '',
        started_at: '',
        ended_at: '',
        processed_dir_path: '',
        data_collect_history_gateways: [
          {
            data_collect_history_id: -1,
            gateway_id: '',
            log_level: -1,
            data_collect_history_handlers: [
              {
                data_collect_history_id: -1,
                gateway_id: '',
                handler_id: '',
                handler_type: '',
                adc_serial_num: -1,
                sampling_frequency: '',
                sampling_ch_num: -1,
                filewrite_time: '',
                is_primary: false,
                data_collect_history_sensors: [
                  {
                    data_collect_history_id: -1,
                    handler_id: '',
                    sensor_id: '',
                    sensor_name: '',
                    sensor_type_id: '',
                    slope: '',
                    intercept: '',
                    start_point_dsl: '',
                    max_point_dsl: '',
                    break_point_dsl: '',
                  },
                ],
              },
            ],
          },
        ],
      },
      headers: [
        {
          text: '機器ID',
          align: 'start',
          value: 'machine_id',
        },
        {
          text: '機器名',
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
        // TODO: primaryハンドラーの値に設定
        {
          text: 'サンプリングレート(Hz)',
          value:
            'data_collect_history_gateways[0].data_collect_history_handlers[0].sampling_frequency',
        },
        // TODO: primaryハンドラーの値に設定
        {
          text: 'チャネル数',
          value:
            'data_collect_history_gateways[0].data_collect_history_handlers[0].sampling_ch_num',
        },
        { text: 'アクション', value: 'actions', sortable: false },
      ],
      detailHeaders: [
        {
          text: 'センサーID',
          value: 'sensor_id',
        },
        {
          text: 'センサー名',
          value: 'sensor_name',
        },
        {
          text: 'センサータイプ',
          value: 'sensor_type_id',
        },
        {
          text: '校正（傾き）',
          value: 'slope',
        },
        {
          text: '校正（切片）',
          value: 'intercept',
        },
        {
          text: '荷重開始点DSL',
          value: 'start_point_dsl',
          width: '300px',
        },
        {
          text: '最大荷重点DSL',
          value: 'max_point_dsl',
          width: '300px',
        },
        {
          text: '破断点DSL',
          value: 'break_point_dsl',
          width: '300px',
        },
      ],
      defaultItem: {
        id: -1,
        machine_id: '',
        machine_name: '',
        machine_type_id: '',
        started_at: '',
        ended_at: '',
        processed_dir_path: '',
        data_collect_history_gateways: [
          {
            data_collect_history_id: -1,
            gateway_id: '',
            log_level: -1,
            data_collect_history_handlers: [
              {
                data_collect_history_id: -1,
                gateway_id: '',
                handler_id: '',
                handler_type: '',
                adc_serial_num: -1,
                sampling_frequency: '',
                sampling_ch_num: -1,
                filewrite_time: '',
                is_primary: false,
                data_collect_history_sensors: [
                  {
                    data_collect_history_id: -1,
                    handler_id: '',
                    sensor_id: '',
                    sensor_name: '',
                    sensor_type_id: '',
                    slope: '',
                    intercept: '',
                    start_point_dsl: '',
                    max_point_dsl: '',
                    break_point_dsl: '',
                  },
                ],
              },
            ],
          },
        ],
      },
      search: '',
      history: [],
      rules: {
        required: (value) => !!value || value === 0 || '必須です。',
        floatType: (value) =>
          (value >= -10000.0 && value <= 10000.0) ||
          '-10000.0～10000.0のみ使用可能です。',
        frequencyRange: (value) =>
          (value >= 1 && value <= 100000) || '1~100,000のみ使用可能です。',
      },
    }
  },

  created: function() {
    this.fetchTableData()
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

  methods: {
    errorSnackbar(message) {
      this.$store.commit('setShowErrorSnackbar', true)
      this.$store.commit('setErrorHeader', message.statusText)
      this.$store.commit('setErrorMsg', message.data.detail)
    },

    fetchTableData: async function() {
      const client = createBaseApiClient()
      await client
        .get(DATA_COLLECT_HISTORY_API_URL)
        .then((res) => {
          if (res.data.length === 0) {
            this.history = []
            return
          }
          // 日付文字列を表示用にフォーマット
          this.history = res.data.map((obj) => {
            obj.started_at = formatJST(obj.started_at)

            if (obj.ended_at !== null) {
              obj.ended_at = formatJST(obj.ended_at)
            }
            return obj
          })
        })
        .catch((e) => {
          console.log(e.response.data.detail)
          this.errorSnackbar(e.response)
        })
    },

    // 編集ダイアログ表示。itemはテーブルで選択したレコードのオブジェクト。
    editItem(item) {
      this.editedIndex = this.history.indexOf(item)
      this.editedItem = Object.assign({}, JSON.parse(JSON.stringify(item)))
      this.dialog = true
    },

    // [保存] 押下時の処理（update）
    save: async function() {
      // form_groupと名付けたv-formを参照し、検証してエラーがあれば何もしない。
      if (!this.$refs.form_group.validate()) {
        return
      }

      const client = createBaseApiClient()

      const url = DATA_COLLECT_HISTORY_API_URL + this.editedItem.id
      const body = {
        data_collect_history_gateways: this.editedItem
          .data_collect_history_gateways,
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
    },

    // 編集ダイアログclose
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
      this.editedIndex = this.history.indexOf(item)
      this.editedItem = Object.assign({}, item)
      this.dialogDelete = true
    },

    // 削除
    deleteItemConfirm: async function() {
      const url = DATA_COLLECT_HISTORY_API_URL + this.editedItem.id

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
