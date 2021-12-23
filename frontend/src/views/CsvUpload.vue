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
            v-model="files"
            accept=".csv"
            color="primary"
            counter
            height="200"
            label="csvファイルを選択、またはドラッグ＆ドロップしてください。            "
            multiple
            outlined
            placeholder="※ここにテキスト表示可能"
            prepend-icon=""
            :show-size="1000"
            :background-color="isDragging ? 'primary' : 'null'"
          >
            <template v-slot:selection="{ index, text }">
              <v-chip v-if="index < 6" color="primary" dark label large close>
                <v-icon left>
                  mdi-file
                </v-icon>
                {{ text }}
              </v-chip>
              <span
                v-else-if="index === 6"
                class="overline grey--text text--darken-3 mx-2"
                >+{{ files.length - 6 }} File(s)</span
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
            :time-picker-props="timeProps"
            @input="CollectDatetime = $event"
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
              files.length === 0 ||
              machineId === null ||
              CollectDatetime === null
          "
          :loading="running"
          >アップロード</v-btn
        >
      </v-row>
    </v-container>
  </v-app>
</template>

<script>
import { createBaseApiClient } from '@/api/apiBase'
import MachineSelect from '@/components/MachineSelect.vue'

export default {
  components: {
    MachineSelect,
  },

  data: () => ({
    files: [],
    isDragging: false,
    dragCount: 0,
    CollectDatetime: null,
    textProps: {
      dense: true,
      clearable: true,
      outlined: true,
      // appendIcon: 'mdi-calendar-clock',
    },
    timeProps: {
      useSeconds: true,
      format: '24hr',
    },
    machineId: null,
    running: false,
    snackbar: false,
    snackbarMessage: '',
  }),
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

    // アップロードボタン押下
    upload: async function() {
      this.running = true

      const postData = {
        machine_id: this.machineId,
        datetime: this.CollectDatetime,
        files: this.files,
      }

      const client = createBaseApiClient()
      const url = 'test'

      await client
        .post(url, postData)
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
  },
}
</script>
