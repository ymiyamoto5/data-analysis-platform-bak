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
        <v-dialog v-model="dialog" max-width="700px">
          <v-card>
            <v-card-title>
              <span class="text-h5">編集</span>
            </v-card-title>

            <v-card-text>
              <v-form ref="form_group">
                <v-text-field
                  v-model="editedItem.sampling_frequency"
                  :rules="[rules.required, rules.frequencyRange]"
                  label="サンプリングレート"
                ></v-text-field>

                <v-data-table
                  :headers="detailHeaders"
                  :items="editedItem.data_collect_history_details"
                >
                  <template v-slot:[`item.base_volt`]="props">
                    <v-text-field
                      v-model="props.item.base_volt"
                      :rules="[rules.floatType]"
                    ></v-text-field>
                  </template>
                  <template v-slot:[`item.base_load`]="props">
                    <v-text-field
                      v-model="props.item.base_load"
                      :rules="[rules.floatType]"
                    ></v-text-field>
                  </template>
                  <template v-slot:[`item.initial_volt`]="props">
                    <v-text-field
                      v-model="props.item.initial_volt"
                      :rules="[rules.floatType]"
                    ></v-text-field>
                  </template>
                </v-data-table>
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
import { formatDate } from '@/common/common'

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
        started_at: '',
        ended_at: '',
        sampling_frequency: 0,
        sampling_ch_num: 0,
        data_collect_history_details: [],
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
        {
          text: 'サンプリングレート(Hz)',
          value: 'sampling_frequency',
        },
        {
          text: 'チャネル数',
          value: 'sampling_ch_num',
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
          text: '基準電圧',
          value: 'base_volt',
        },
        {
          text: '基準圧力',
          value: 'base_load',
        },
        {
          text: '初期電圧',
          value: 'initial_volt',
        },
      ],
      defaultItem: {
        sampling_frequency: 0,
        data_collect_history_details: [
          {
            data_collect_history_id: -1,
            sensor_id: '',
            sensor_name: '',
            sensor_type_id: -1,
            base_load: null,
            base_volt: null,
            initial_volt: null,
          },
        ],
      },
      search: '',
      history: [],
      rules: {
        required: (value) => !!value || '必須です。',
        floatType: (value) =>
          (value >= 0.0 && value <= 100.0) || '0.0～100.0のみ使用可能です。',
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
    fetchTableData: async function() {
      const client = createBaseApiClient()
      await client
        .get(DATA_COLLECT_HISTORY_API_URL)
        .then((res) => {
          if (res.data.length === 0) {
            return
          }
          // 日付文字列を表示用にフォーマット
          this.history = res.data.map((obj) => {
            obj.started_at = formatDate(obj.started_at)

            if (obj.ended_at !== null) {
              obj.ended_at = formatDate(obj.ended_at)
            }
            return obj
          })
        })
        .catch((e) => {
          console.log(e.response.data.detail)
        })
    },

    // 編集ダイアログ表示。itemはテーブルで選択したレコードのオブジェクト。
    editItem(item) {
      this.editedIndex = this.history.indexOf(item)
      this.editedItem = Object.assign({}, item)
      this.dialog = true
    },

    // [保存] 押下時の処理（update）
    save: async function() {
      // form_groupと名付けたv-formを参照し、検証してエラーがあれば何もしない。
      if (!this.$refs.form_group.validate()) {
        return
      }

      const client = createBaseApiClient()

      // 空文字の時nullに置き換え
      this.editedItem.data_collect_history_details.map((obj) => {
        obj.base_volt = obj.base_volt === '' ? null : obj.base_volt
        obj.base_load = obj.base_load === '' ? null : obj.base_load
        obj.initial_volt = obj.initial_volt === '' ? null : obj.initial_volt
        return obj
      })

      const url = DATA_COLLECT_HISTORY_API_URL + this.editedItem.id
      const body = {
        sampling_frequency: this.editedItem.sampling_frequency,
        data_collect_history_details: this.editedItem
          .data_collect_history_details,
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
      const url = DATA_COLLECT_HISTORY_API_URL + this.editedItem.id + '/'

      const client = createBaseApiClient()
      await client
        .delete(url)
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
