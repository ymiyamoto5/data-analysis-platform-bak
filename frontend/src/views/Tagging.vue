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
                <v-text-field
                  v-model="editedItem.tag"
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
              削除してもよいですか？
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
import { formatDate } from '@/common/common'
const TAGS_API_URL = '/api/v1/tags/'

export default {
  data: () => ({
    dialog: false,
    dialogDelete: false,
    headers: [
      {
        text: '日時',
        align: 'start',
        value: 'occurred_at',
      },
      { text: 'タグ', value: 'tag' },
      { text: 'アクション', value: 'actions', sortable: false },
    ],
    tags: [],
    editedIndex: -1,
    editedItem: {
      occurred_at: '',
      tag: '',
    },
    defaultItem: {
      occurred_at: '',
      tag: '',
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
    this.fetchMachineTypes()
  },

  methods: {
    errorDialog(message) {
      this.$store.commit('setShowErrorDialog', true)
      this.$store.commit('setErrorMsg', message)
    },

    fetchTableData: async function() {
      const client = createBaseApiClient()
      await client
        .get(TAGS_API_URL)
        .then((res) => {
          if (res.data.length === 0) {
            return
          }
          // 日付文字列を表示用にフォーマット
          this.tags = res.data.map((obj) => {
            obj.occurred_at = formatDate(obj.occurred_at)
            return obj
          })
        })
        .catch((e) => {
          console.log(e.response.data.detail)
          this.errorDialog(e.response.data.detail)
        })
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
      let body = {}
      const client = createBaseApiClient()

      // update
      if (this.editedIndex > -1) {
        url = TAGS_API_URL + this.editedItem.tag_id + '/'
        body = {
          occurred_at: this.editedItem.occurred_at,
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
            this.errorDialog(e.response.data.detail)
          })
      }
      // insert
      else {
        url = TAGS_API_URL
        body = {
          occurred_at: this.editedItem.occurred_at,
          tag: this.editedItem.tag,
        }
        await client
          .post(url, body)
          .then(() => {
            this.dialog = false
            this.fetchTableData()
          })
          .catch((e) => {
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
      this.editedIndex = this.machines.indexOf(item)
      this.editedItem = Object.assign({}, item)
      this.dialogDelete = true
    },

    // 削除
    deleteItemConfirm: async function() {
      const url = TAGS_API_URL + this.editedItem.tag_id + '/'

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
