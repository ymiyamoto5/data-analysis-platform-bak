<template>
  <v-data-table
    :headers="headers"
    :items="tags"
    sort-by="occurred_at"
    class="elevation-1"
  >
    <template v-slot:top>
      <v-toolbar flat>
        <v-toolbar-title>タグ</v-toolbar-title>
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
                <v-menu
                  ref="occurred_date_menu"
                  v-model="editedItem.occurred_date_menu"
                  :close-on-content-click="false"
                  transition="scale-transition"
                  offset-y
                >
                  <template v-slot:activator="{ on, attrs }">
                    <v-text-field
                      v-model="editedItem.occurred_dateFormatted"
                      :rules="[rules.required]"
                      label="発生日"
                      prepend-icon="mdi-calendar"
                      readonly
                      v-bind="attrs"
                      v-on="on"
                    ></v-text-field>
                  </template>
                  <v-date-picker
                    v-model="occurred_date"
                    no-title
                    scrollable
                    width="450px"
                    color="primary"
                  >
                    <v-spacer></v-spacer>
                    <v-btn
                      text
                      color="primary"
                      @click="editedItem.occurred_date_menu = false"
                    >
                      キャンセル
                    </v-btn>
                    <v-btn
                      text
                      color="primary"
                      @click="$refs.occurred_date_menu.save(occurred_date)"
                    >
                      OK
                    </v-btn>
                  </v-date-picker>
                </v-menu>

                <v-menu
                  ref="occurred_time_menu"
                  v-model="editedItem.occurred_time_menu"
                  :close-on-content-click="false"
                  :return-value.sync="occurred_time"
                  transition="scale-transition"
                  offset-y
                >
                  <template v-slot:activator="{ on, attrs }">
                    <v-text-field
                      v-model="editedItem.occurred_time"
                      :rules="[rules.required]"
                      label="発生時刻"
                      prepend-icon="mdi-clock-time-four-outline"
                      readonly
                      v-bind="attrs"
                      v-on="on"
                    ></v-text-field>
                  </template>
                  <v-time-picker
                    v-if="editedItem.occurred_time_menu"
                    v-model="editedItem.occurred_time"
                    format="24hr"
                    use-seconds
                    full-width
                    @click:second="$refs.occurred_time_menu.save(occurred_time)"
                  ></v-time-picker>
                </v-menu>

                <v-menu
                  ref="ended_date_menu"
                  v-model="editedItem.ended_date_menu"
                  :close-on-content-click="false"
                  transition="scale-transition"
                  offset-y
                >
                  <template v-slot:activator="{ on, attrs }">
                    <v-text-field
                      v-model="editedItem.ended_dateFormatted"
                      label="終了日"
                      prepend-icon="mdi-calendar"
                      readonly
                      clearable
                      v-bind="attrs"
                      v-on="on"
                      @input="resetEndedTime"
                    ></v-text-field>
                  </template>
                  <v-date-picker
                    v-model="ended_date"
                    no-title
                    scrollable
                    width="450px"
                    color="primary"
                  >
                    <v-spacer></v-spacer>
                    <v-btn
                      text
                      color="primary"
                      @click="editedItem.ended_date_menu = false"
                    >
                      キャンセル
                    </v-btn>
                    <v-btn
                      text
                      color="primary"
                      @click="$refs.ended_date_menu.save(ended_date)"
                    >
                      OK
                    </v-btn>
                  </v-date-picker>
                </v-menu>

                <v-menu
                  ref="ended_time_menu"
                  v-model="editedItem.ended_time_menu"
                  :close-on-content-click="false"
                  :return-value.sync="ended_time"
                  transition="scale-transition"
                  offset-y
                >
                  <template v-slot:activator="{ on, attrs }">
                    <v-text-field
                      v-model="editedItem.ended_time"
                      :rules="[endedTimeRequired]"
                      label="終了時刻"
                      prepend-icon="mdi-clock-time-four-outline"
                      readonly
                      v-bind="attrs"
                      v-on="on"
                      :disabled="editedItem.ended_dateFormatted === null"
                    ></v-text-field>
                  </template>
                  <v-time-picker
                    v-if="editedItem.ended_time_menu"
                    v-model="editedItem.ended_time"
                    format="24hr"
                    use-seconds
                    full-width
                    @click:second="$refs.ended_time_menu.save(ended_time)"
                  ></v-time-picker>
                </v-menu>

                <v-text-field
                  v-model="editedItem.tag"
                  :rules="[rules.required, rules.counter]"
                  label="タグ"
                ></v-text-field>
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
              タグ：{{ editedItem.tag }} を削除してもよいですか？
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
    <template v-slot:[`item.ended_at`]="{ item }">
      {{ formatNull(item.ended_at) }}
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
import { formatJST, formatUTC, formatDate, formatTime } from '@/common/common'
const TAGS_API_URL = '/api/v1/tags/'

export default {
  data: (vm) => ({
    dialog: false,
    dialogDelete: false,
    headers: [
      {
        text: '発生日時',
        align: 'start',
        value: 'occurred_at',
      },
      {
        text: '終了日時',
        value: 'ended_at',
      },
      { text: 'タグ', value: 'tag' },
      { text: 'アクション', value: 'actions', sortable: false },
    ],
    tags: [],
    occurred_date: new Date(Date.now() - new Date().getTimezoneOffset() * 60000)
      .toISOString()
      .substr(0, 10),
    ended_date: null,
    editedIndex: -1,
    editedItem: {
      id: '',
      occurred_at: '',
      ended_at: null,
      tag: '',
      occurred_dateFormatted: vm.formatDate(
        new Date(Date.now() - new Date().getTimezoneOffset() * 60000)
          .toISOString()
          .substr(0, 10),
      ),
      occurred_date_menu: false,
      occurred_time: '00:00:00',
      occurred_time_menu: false,
      ended_dateFormatted: null,
      ended_date_menu: false,
      ended_time: null,
      ended_time_menu: false,
    },
    defaultItem: {
      id: '',
      occurred_at: '',
      ended_at: null,
      tag: '',
      occurred_dateFormatted: vm.formatDate(
        new Date(Date.now() - new Date().getTimezoneOffset() * 60000)
          .toISOString()
          .substr(0, 10),
      ),
      occurred_date_menu: false,
      occurred_time: '00:00:00',
      occurred_time_menu: false,
      ended_dateFormatted: null,
      ended_date_menu: false,
      ended_time: null,
      ended_time_menu: false,
    },
    rules: {
      required: (value) => !!value || '必須です。',
      counter: (value) => value.length <= 255 || '最大255文字です。',
    },
  }),

  computed: {
    formTitle() {
      return this.editedIndex === -1 ? '新規作成' : '編集'
    },
    readOnlyID() {
      return this.editedIndex === -1 ? { disabled: false } : { disabled: true }
    },
    // validation
    endedTimeRequired() {
      let rule = true
      if (this.editedItem.ended_dateFormatted !== null) {
        rule = (value) => value !== null || '必須です。'
      }
      return rule
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
    occurred_date() {
      this.editedItem.occurred_dateFormatted = this.formatDate(
        this.occurred_date,
      )
    },
    ended_date() {
      this.editedItem.ended_dateFormatted = this.formatDate(this.ended_date)
    },
  },

  created() {
    this.fetchTableData()
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
        .get(TAGS_API_URL)
        .then((res) => {
          if (res.data.length === 0) {
            this.tags = []
            return
          }
          // 日付文字列を表示用にフォーマット
          this.tags = res.data.map((obj) => {
            obj.occurred_dateFormatted = formatDate(obj.occurred_at)
            obj.occurred_time = formatTime(obj.occurred_at)
            obj.occurred_at = formatJST(obj.occurred_at)
            if (obj.ended_at === null) {
              obj.ended_dateFormatted = this.defaultItem.ended_dateFormatted
              obj.ended_time = this.defaultItem.ended_time
              obj.ended_at = this.defaultItem.ended_at
            } else {
              obj.ended_dateFormatted = formatDate(obj.ended_at)
              obj.ended_time = formatTime(obj.ended_at)
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

    // 終了日時のNULL値を表示用にフォーマット
    formatNull(ended_at) {
      return ended_at !== null ? ended_at : '-'
    },

    // 新規作成 or 編集ダイアログ表示。itemはテーブルで選択したレコードのオブジェクト。
    editItem(item) {
      this.editedIndex = this.tags.indexOf(item)
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
      let occurred_datetime = formatUTC(
        this.editedItem.occurred_dateFormatted +
          ' ' +
          this.editedItem.occurred_time,
      )
      let ended_datetime = null
      if (this.editedItem.ended_dateFormatted !== null) {
        ended_datetime = formatUTC(
          this.editedItem.ended_dateFormatted +
            ' ' +
            this.editedItem.ended_time,
        )
      }

      let body = {}
      const client = createBaseApiClient()

      // update
      if (this.editedIndex > -1) {
        url = TAGS_API_URL + this.editedItem.id
        body = {
          occurred_at: occurred_datetime,
          ended_at: ended_datetime,
          tag: this.editedItem.tag,
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
        url = TAGS_API_URL
        body = {
          occurred_at: occurred_datetime,
          ended_at: ended_datetime,
          tag: this.editedItem.tag,
        }
        await client
          .post(url, body)
          .then(() => {
            this.dialog = false
            this.fetchTableData()
          })
          .catch((e) => {
            this.errorSnackbar(e.response)
          })
      }
    },

    // 終了日がnullになったとき、終了時刻を未設定の状態にする
    resetEndedTime: async function() {
      if (this.editedItem.ended_dateFormatted === null) {
        this.editedItem.ended_time = null
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
      this.editedIndex = this.tags.indexOf(item)
      this.editedItem = Object.assign({}, item)
      this.dialogDelete = true
    },

    // 削除
    deleteItemConfirm: async function() {
      const url = TAGS_API_URL + this.editedItem.id

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

    formatDate(date) {
      if (!date) return null

      const [year, month, day] = date.split('-')
      return `${year}/${month}/${day}`
    },
  },
}
</script>
