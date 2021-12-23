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
            color="primary"
            counter
            label="csvファイルを選択、またはドラッグ＆ドロップしてください。"
            multiple
            placeholder="Select your files"
            prepend-icon=""
            outlined
            :show-size="1000"
            :background-color="isDragging ? 'blue' : 'null'"
          >
            <template v-slot:selection="{ index, text }">
              <v-chip v-if="index < 2" color="primary" dark label small>{{
                text
              }}</v-chip>
              <span
                v-else-if="index === 2"
                class="overline grey--text text--darken-3 mx-2"
                >+{{ files.length - 2 }} File(s)</span
              >
            </template>
          </v-file-input>
        </v-col>
      </v-row>
      <v-row dense>
        <v-col cols="5">
          <MachineSelect @input="setMachine"></MachineSelect>
        </v-col>
      </v-row>

      <v-row dense>
        <v-col cols="5">
          <v-datetime-picker
            v-model="datetime"
            label="採取日時"
            dateFormat="yyyy/MM/dd"
            timeFormat="HH:mm:ss"
          >
            <template slot="dateIcon">
              <v-icon>mdi-calendar</v-icon>
            </template>
            <template slot="timeIcon">
              <v-icon>mdi-clock-outline</v-icon>
            </template>
          </v-datetime-picker>
        </v-col>
      </v-row>

      <v-row justify="center">
        <v-btn color="primary">アップロード</v-btn>
      </v-row>
    </v-container>
  </v-app>
</template>

<script>
// import { createBaseApiClient } from '@/api/apiBase'
import MachineSelect from '@/components/MachineSelect.vue'

export default {
  // name: 'DragAndDrop',
  components: {
    MachineSelect,
  },

  data: () => ({
    files: [],
    isDragging: false,
    dragCount: 0,
  }),
  methods: {
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
  },
}
</script>

<style scoped>
#title {
  margin: 15px;
}
</style>
