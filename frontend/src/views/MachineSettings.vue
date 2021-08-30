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
              <v-container>
                <v-row>
                  <v-col cols="12" sm="6" md="4">
                    <v-text-field
                      v-model="editedItem.machine_id"
                      label="機器ID"
                      v-bind="readOnlyID"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12" sm="6" md="4">
                    <v-text-field
                      v-model="editedItem.machine_name"
                      label="機器名"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12" sm="6" md="4">
                    <v-select
                      item-text="machine_type_name"
                      item-value="id"
                      :items="machineTypes"
                      label="機種"
                      @change="setMachineTypes"
                    >
                    </v-select>
                  </v-col>
                </v-row>
              </v-container>
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
            <v-card-title class="text-h5"
              >本当に削除してもよいですか？</v-card-title
            >
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
    <template v-slot:item.actions="{ item }">
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
    machineTypes: [],
  }),

  computed: {
    formTitle() {
      return this.editedIndex === -1 ? '新規作成' : '編集'
    },
    readOnlyID() {
      return this.editedIndex === -1 ? { disabled: false } : { disabled: true }
    },
  },

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
      let data = []
      await client
        .get(MACHINE_TYPES_API_URL)
        .then((res) => {
          if (res.data.length === 0) {
            return
          }
          data = res.data
          this.machineTypes = data
        })
        .catch((e) => {
          console.log(e.response.data.message)
          this.confirm_dialog(e.response.data.message)
        })
    },

    setMachineTypes(value) {
      this.editedItem.machine_type_id = value
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
          console.log(e.response.data.message)
          this.confirm_dialog(e.response.data.message)
        })
    },

    editItem(item) {
      this.editedIndex = this.machines.indexOf(item)
      this.editedItem = Object.assign({}, item)
      this.dialog = true
    },

    deleteItem(item) {
      this.editedIndex = this.machines.indexOf(item)
      this.editedItem = Object.assign({}, item)
      this.dialogDelete = true
    },

    deleteItemConfirm() {
      this.machines.splice(this.editedIndex, 1)
      this.closeDelete()
    },

    close() {
      this.dialog = false
      this.$nextTick(() => {
        this.editedItem = Object.assign({}, this.defaultItem)
        this.editedIndex = -1
      })
    },

    closeDelete() {
      this.dialogDelete = false
      this.$nextTick(() => {
        this.editedItem = Object.assign({}, this.defaultItem)
        this.editedIndex = -1
      })
    },

    // [保存] 押下時の処理（update or insert）
    save: async function() {
      let postUrl = ''
      let postData = {}
      // update
      if (this.editedIndex > -1) {
        postUrl =
          MACHINES_API_URL + '/' + this.editedItem.machine_id + '/update'
        postData = {
          machine_name: this.editedItem.machine_name,
          machine_type_id: this.editedItem.machine_type_id,
        }
      }
      // insert
      else {
        postUrl = MACHINES_API_URL
        postData = {
          machine_id: this.editedItem.machine_id,
          machine_name: this.editedItem.machine_name,
          machine_type_id: this.editedItem.machine_type_id,
        }
      }

      const client = createBaseApiClient()
      await client
        .post(postUrl, postData)
        .then(() => {
          this.close()
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
