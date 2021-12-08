<template>
  <v-app>
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
                  <template v-if="editedIndex !== -1">
                    <v-checkbox
                      v-model="editedItem.auto_cut_out_shot"
                      hide-details
                      label="自動ショット切り出し"
                      @change="resetCutOutShot"
                    ></v-checkbox>
                    <v-text-field
                      v-model="editedItem.start_displacement"
                      :disabled="!editedItem.auto_cut_out_shot"
                      :rules="[autoCutOutShotRequired, rules.displacementRange]"
                      label="切り出し開始変位値"
                    ></v-text-field>
                    <v-text-field
                      v-model="editedItem.end_displacement"
                      :disabled="!editedItem.auto_cut_out_shot"
                      :rules="[autoCutOutShotRequired, rules.displacementRange]"
                      label="切り出し終了変位値"
                    ></v-text-field>
                    <v-text-field
                      v-model="editedItem.margin"
                      :disabled="!editedItem.auto_cut_out_shot"
                      :rules="[autoCutOutShotRequired, rules.marginRange]"
                      label="マージン"
                    >
                      <template v-slot:append-outer>
                        <v-tooltip bottom>
                          <template v-slot:activator="{ on }">
                            <v-icon v-on="on">
                              mdi-help-circle-outline
                            </v-icon>
                          </template>
                          <div>
                            ショット切り出し開始後の変位値上昇に対するマージン。ショット切り出しにおいて変位値は単調減少であることを前提としているが、ノイズ等の影響で単調減少しないときのための調整パラメータ。
                            <br />
                            例）ショット切り出し開始しきい値を 100.0、マージン
                            0.0の場合、変位値が 100.0
                            に到達した後にノイズサンプルで
                            100.1が計測されるとショット終了とみなして切り出しが終了してしまう。
                            <br />
                            マージンを0.1
                            に設定すると、100.1が計測されたとしてもショット切り出しを終了しない。
                          </div>
                        </v-tooltip>
                      </template>
                    </v-text-field>
                    <v-checkbox
                      v-model="editedItem.auto_predict"
                      :disabled="!editedItem.auto_cut_out_shot"
                      hide-details
                      label="自動予測"
                      @change="resetPredict"
                    ></v-checkbox>
                    <v-select
                      v-model="editedItem.predict_model"
                      :disabled="!editedItem.auto_predict"
                      :rules="[autoPredictRequired]"
                      :items="models"
                      label="モデル"
                      @input="setModel"
                    >
                    </v-select>
                    <v-select
                      v-model="editedItem.model_version"
                      :disabled="!editedItem.auto_predict"
                      :rules="[autoPredictRequired]"
                      :items="versions"
                      label="バージョン"
                    >
                    </v-select>
                  </template>
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
      <template v-slot:[`item.auto_cut_out_shot`]="{ item }">
        {{ formatBool(item.auto_cut_out_shot) }}
      </template>
      <template v-slot:[`item.auto_predict`]="{ item }">
        {{ formatBool(item.auto_predict) }}
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
    <v-snackbar v-model="snackbar" timeout="10000" top color="error">
      <h3>{{ snackbarHeader }}</h3>
      {{ snackbarMessage }}
      <template v-slot:action="{ attrs }">
        <v-btn color="white" text v-bind="attrs" @click="snackbar = false">
          Close
        </v-btn>
      </template>
    </v-snackbar>
  </v-app>
</template>

<script>
import { createBaseApiClient } from '@/api/apiBase'
const MACHINES_API_URL = '/api/v1/machines/'
const MACHINE_TYPES_API_URL = '/api/v1/machine_types/'
const MODELS_API_URL = '/api/v1/models/'
const MODEL_VERSIONS_API_URL = '/api/v1/models/versions'

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
      {
        text: '自動ショット切り出し',
        value: 'auto_cut_out_shot',
        width: '15%',
      },
      { text: '自動予測', value: 'auto_predict', width: '10%' },
      { text: 'アクション', value: 'actions', sortable: false, width: '10%' },
    ],
    machines: [],
    editedIndex: -1,
    editedItem: {
      machine_id: '',
      machine_name: '',
      machine_type_id: 0,
      auto_cut_out_shot: false,
      start_displacement: '',
      end_displacement: '',
      margin: '',
      auto_predict: false,
      predict_model: '',
      model_version: '',
    },
    defaultItem: {
      machine_id: '',
      machine_name: '',
      machine_type_id: 0,
      auto_cut_out_shot: false,
      start_displacement: '',
      end_displacement: '',
      margin: '',
      auto_predict: false,
      predict_model: '',
      model_version: '',
    },
    machineTypes: [],
    models: [],
    selectedModel: '',
    versions: [],
    snackbar: false,
    snackbarHeader: '',
    snackbarMessage: '',
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
      displacementRange: (value) =>
        (value >= 0.0 && value <= 100.0) || '0.0～100.0のみ使用可能です。',
      marginRange: (value) =>
        (value >= 0.0 && value <= 10000.0) || '0.0～10000.0のみ使用可能です。',
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
    autoCutOutShotRequired() {
      let rule = true
      if (this.editedItem.auto_cut_out_shot) {
        rule = (value) => (value !== null && value !== '') || '必須です。'
      }
      return rule
    },
    autoPredictRequired() {
      let rule = true
      if (this.editedItem.auto_predict) {
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
    selectedModel: function() {
      this.fetchVersions()
    },
  },

  created() {
    this.fetchTableData()
    this.fetchMachineTypes()
    this.fetchModels()
  },

  methods: {
    errorSnackbar(message) {
      this.$store.commit('setShowErrorSnackbar', true)
      this.$store.commit('setErrorHeader', message.statusText)
      this.$store.commit('setErrorMsg', message.data.detail)
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
          this.errorSnackbar(e.response)
        })
    },

    fetchModels: async function() {
      const client = createBaseApiClient()
      await client
        .get(MODELS_API_URL)
        .then((res) => {
          if (res.data.length === 0) {
            return
          }
          this.models = res.data
        })
        .catch((e) => {
          console.log(e.response.data.detail)
          this.errorSnackbar(e.response)
        })
    },
    setModel(model) {
      this.selectedModel = model
    },
    fetchVersions: async function() {
      const client = createBaseApiClient()
      await client
        .get(MODEL_VERSIONS_API_URL, {
          params: { model: this.selectedModel },
        })
        .then((res) => {
          if (res.data.length === 0) {
            return
          }
          this.versions = res.data
        })
        .catch((e) => {
          console.log(e.response.data.detail)
          this.errorSnackbar(e.response)
        })
    },

    // テーブル用データ取得
    fetchTableData: async function() {
      const client = createBaseApiClient()
      let data = []
      await client
        .get(MACHINES_API_URL)
        .then((res) => {
          if (res.data.length === 0) {
            this.machines = []
            return
          }
          data = res.data
          this.machines = data
        })
        .catch((e) => {
          console.log(e.response.data.detail)
          this.errorSnackbar(e.response)
        })
    },

    // 自動ショット切り出しと自動予測のbool値を表示用にフォーマット
    formatBool(bool) {
      return bool ? 'ON' : 'OFF'
    },

    // 新規作成 or 編集ダイアログ表示。itemはテーブルで選択したレコードのオブジェクト。
    editItem(item) {
      this.editedIndex = this.machines.indexOf(item)
      this.editedItem = Object.assign({}, item)
      // 編集ダイアログ表示のとき、予測モデルが設定済みの場合はバージョンを取得する
      if (this.editedItem.predict_model !== null) {
        this.selectedModel = this.editedItem.predict_model
      }
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
        url = MACHINES_API_URL + this.editedItem.machine_id
        body = {
          machine_name: this.editedItem.machine_name,
          machine_type_id: this.editedItem.machine_type_id,
          auto_cut_out_shot: this.editedItem.auto_cut_out_shot,
          start_displacement: this.editedItem.start_displacement,
          end_displacement: this.editedItem.end_displacement,
          margin: this.editedItem.margin,
          auto_predict: this.editedItem.auto_predict,
          predict_model: this.editedItem.predict_model,
          model_version: this.editedItem.model_version,
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
            console.log(e.response.data.detail)
            this.errorSnackbar(e.response)
          })
      }
    },

    // 自動ショット切り出しがfalseになったとき、切り出し変位値とマージンと自動予測を未設定の状態にする
    resetCutOutShot: async function() {
      if (!this.editedItem.auto_cut_out_shot) {
        this.editedItem.start_displacement = null
        this.editedItem.end_displacement = null
        this.editedItem.margin = null
      }

      if (this.editedItem.auto_predict) {
        this.editedItem.auto_predict = false
        this.resetPredict()
      }
    },

    // 自動予測がfalseになったとき、モデルとバージョンを未設定の状態にする
    resetPredict: async function() {
      if (!this.editedItem.auto_predict) {
        this.editedItem.predict_model = null
        this.editedItem.model_version = null
        this.selectedModel = ''
        this.versions = []
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
      const url = MACHINES_API_URL + this.editedItem.machine_id

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
