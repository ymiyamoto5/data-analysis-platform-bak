<template>
  <v-data-table
    :headers="headers"
    :items="machines"
    sort-by="machine_id"
    class="elevation-1"
  >
    <template v-slot:top>
      <v-toolbar flat>
        <v-toolbar-title>機器管理</v-toolbar-title>
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
                  v-model="editedItem.machine_id"
                  :rules="[rules.required, rules.counter, rules.idPattern]"
                  label="機器ID"
                  v-bind="readOnlyID"
                ></v-text-field>
                <v-text-field
                  v-model="editedItem.machine_name"
                  :rules="[rules.required, rules.counter]"
                  label="機器名"
                ></v-text-field>
                <v-select
                  v-model="editedItem.machine_type_id"
                  :rules="[rules.required]"
                  item-text="machine_type_name"
                  item-value="machine_type_id"
                  :items="machineTypes"
                  label="機種"
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
              機器ID：{{ editedItem.machine_id }} を削除してもよいですか？
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
const MACHINES_API_URL = '/api/v1/machines'
const MACHINE_TYPES_API_URL = '/api/v1/machine_types'

export default {
  data: () => ({
    dialog: false,
    dialogDelete: false,
    headers: [
      {
        text: '機器ID',
        align: 'start',
        value: 'machine_id',
      },
      { text: '機器名', value: 'machine_name' },
      { text: '機種', value: 'machine_type.machine_type_name' },
      { text: 'アクション', value: 'actions', sortable: false },
    ],
    machines: [],
    editedIndex: -1,
    editedItem: {
      machine_id: '',
      machine_name: '',
      machine_type_id: 0,
    },
    defaultItem: {
      machine_id: '',
      machine_name: '',
      machine_type_id: 0,
    },
    machineTypes: [],
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

    // ドロップダウンリスト用データ取得
    fetchMachineTypes: async function() {
      const client = createBaseApiClient()
      await client
        .get(MACHINE_TYPES_API_URL)
        .then((res) => {
          if (res.data.length === 0) {
            return
          }
          this.machineTypes = res.data
        })
        .catch((e) => {
          console.log(e.response.data.detail)
          this.errorDialog(e.response.data.detail)
        })
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
          this.machines = data
        })
        .catch((e) => {
          console.log(e.response.data.detail)
          this.errorDialog(e.response.data.detail)
        })
    },

    // 新規作成 or 編集ダイアログ表示。itemはテーブルで選択したレコードのオブジェクト。
    editItem(item) {
      this.editedIndex = this.machines.indexOf(item)
      this.editedItem = Object.assign({}, item)
      this.dialog = true
    },

    // [保存] 押下時の処理（update or insert）
    save: async function() {
      // form_groupと名付けたv-formを参照し、検証してエラーがあれば何もしない。
      if (!this.$refs.form_group.validate()) {
        return
      }

      const client = createBaseApiClient()
      let url = ''
      let body = {}
      // update
      if (this.editedIndex > -1) {
        url = MACHINES_API_URL + '/' + this.editedItem.machine_id
        body = {
          machine_name: this.editedItem.machine_name,
          machine_type_id: this.editedItem.machine_type_id,
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
        url = MACHINES_API_URL
        body = {
          machine_id: this.editedItem.machine_id,
          machine_name: this.editedItem.machine_name,
          machine_type_id: this.editedItem.machine_type_id,
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
      const url = MACHINES_API_URL + '/' + this.editedItem.machine_id

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
