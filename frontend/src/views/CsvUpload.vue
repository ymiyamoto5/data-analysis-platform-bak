<template>
  <v-app>
    <v-container>
      <v-row
        dense
        class="text-center"
        @dragover.prevent
        @dragenter="onDragEnter"
        @dragleave="onDragLeave"
        @drop="onDrop"
      >
        <v-col cols="7">
          <v-file-input
            ref="file_form"
            v-model="files"
            accept=".csv"
            color="primary"
            counter
            height="200"
            label="csvファイルを選択、またはドラッグ＆ドロップしてください。"
            multiple
            outlined
            prepend-icon=""
            :rules="[rules.fileRequired, rules.filePattern]"
            :show-size="1000"
            :background-color="isDragging ? 'primary' : 'null'"
          >
            <template v-slot:selection="{ index, text }">
              <v-chip
                v-if="index < 10"
                color="primary"
                close
                dark
                label
                small
                @click:close="deleteFile(index)"
              >
                <v-icon left>
                  mdi-file
                </v-icon>
                {{ text }}
              </v-chip>
              <span
                v-else-if="index === 10"
                class="overline grey--text text--darken-3 mx-2"
                >+{{ files.length - 10 }} File(s)</span
              >
            </template>
          </v-file-input>
        </v-col>
      </v-row>

      <v-row dense>
        <v-col cols="5">
          <MachineSelect @input="machineId = $event"></MachineSelect>
        </v-col>
      </v-row>

      <v-row dense>
        <v-col cols="2">
          <v-datetime-picker
            label="採取日時"
            dateime="String"
            dateFormat="YYYY/MM/DD"
            timeFormat="HH:mm:ss"
            clearText="キャンセル"
            :text-field-props="textProps"
            :date-picker-props="dateProps"
            :time-picker-props="timeProps"
            @input="setCollectDatetime"
          >
          </v-datetime-picker>
        </v-col>
      </v-row>

      <v-row justify="center">
        <v-btn
          color="primary"
          @click="upload"
          :disabled="
            running ||
              !validate ||
              machineId === null ||
              collectDatetime === null
          "
          :loading="running"
          >アップロード</v-btn
        >
      </v-row>

      <v-snackbar v-model="snackbar" timeout="5000" top color="success">
        {{ snackbarMessage }}
        <template v-slot:action="{ attrs }">
          <v-btn color="white" text v-bind="attrs" @click="snackbar = false">
            Close
          </v-btn>
        </template>
      </v-snackbar>
    </v-container>
  </v-app>
</template>

<script>
import { createBaseApiClient } from '@/api/apiBase'
import MachineSelect from '@/components/MachineSelect.vue'

const TARGET_DIR_API_URL = '/api/v1/cut_out_shot/target_dir'
const CSV_UPLOAD_API_URL = '/api/v1/csv_upload/'

export default {
  components: {
    MachineSelect,
  },

  data: () => ({
    files: [],
    isDragging: false,
    dragCount: 0,
    validate: false,
    collectDatetime: null,
    formatCollectDatetime: null,
    textProps: {
      dense: true,
      outlined: true,
    },
    dateProps: {
      // color: 'primary',
    },
    timeProps: {
      useSeconds: true,
      format: '24hr',
    },
    machineId: null,
    running: false,
    snackbar: false,
    snackbarMessage: '',
    // validation
    rules: {
      fileRequired: (value) => value.length !== 0 || '必須です。',
      filePattern: (values) => {
        const pattern = /\.csv$/
        for (const index in values) {
          if (!pattern.test(values[index].name)) {
            return 'CSVファイルのみアップロード可能です。'
          }
        }
        return true
      },
    },
  }),

  watch: {
    // アップロードボタンの押下判定をするため、file_formのバリデーションチェック
    files: function() {
      this.validate = this.$refs.file_form.validate()
    },
  },

  methods: {
    errorSnackbar(message) {
      this.$store.commit('setShowErrorSnackbar', true)
      this.$store.commit('setErrorHeader', message.statusText)
      this.$store.commit('setErrorMsg', message.data.detail)
    },

    // https://www.ultra-noob.com/blog/2020/106/
    onDrop(e) {
      e.preventDefault()
      e.stopPropagation()
      this.isDragging = false
      const _files = e.dataTransfer.files
      for (const file in _files) {
        if (!isNaN(file)) {
          //filesはファイル以外のデータが入っており、ファイルの場合のみキー名が数字になるため
          this.files.push(_files[file])
        }
      }
    },
    onDragEnter(e) {
      e.preventDefault()
      this.isDragging = true
      this.dragCount++
    },
    onDragLeave(e) {
      e.preventDefault()
      this.dragCount--
      if (this.dragCount <= 0) {
        this.isDragging = false
      }
    },

    // 採取日時（yyyy/MM/dd hh:mm:ss）選択後、yyyyMMddhhmmssに変換する
    setCollectDatetime(value) {
      this.collectDatetime = value
      if (this.collectDatetime !== null) {
        this.fetchFormatCollectDatetime()
      }
    },
    fetchFormatCollectDatetime: async function() {
      const unixDatetime = Date.parse(this.collectDatetime)

      const client = createBaseApiClient()
      await client
        .get(TARGET_DIR_API_URL, {
          params: {
            target_date_timestamp: unixDatetime,
          },
        })
        .then((res) => {
          if (res.data === null) {
            return
          }
          this.formatCollectDatetime = res.data
        })
        .catch((e) => {
          console.log(e.response.data.detail)
          this.errorSnackbar(e.response)
        })
    },

    // アップロードボタン押下
    upload: async function() {
      this.running = true

      const config = {
        headers: {
          'Content-type': 'multipart/form-data',
        },
      }

      const client = createBaseApiClient()
      let form = new FormData()
      form.append('machine_id', this.machineId)
      form.append('date_time', this.formatCollectDatetime)
      this.files.map((file) => {
        form.append('files', file)
      })
      client
        .post(CSV_UPLOAD_API_URL, form, config)
        .then(() => {
          this.running = false
          this.snackbarMessage = 'アップロードが完了しました'
          this.snackbar = true
        })
        .catch((e) => {
          this.running = false
          console.log(e.response.data.detail)
          this.errorSnackbar(e.response)
        })
    },

    deleteFile(index) {
      this.files.splice(index, 1)
    },
  },
}
</script>
