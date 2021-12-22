<template>
  <v-app>
    <v-card>
      <v-card-title>
        CSVアップロード
      </v-card-title>
      <v-row
        dense
        class="text-center"
        @dragover.prevent
        @dragenter="onDragEnter"
        @dragleave="onDragLeave"
        @drop="onDrop"
      >
        <v-file-input
          v-model="files"
          color="deep-purple accent-4"
          counter
          label="File input"
          multiple
          placeholder="Select your files"
          prepend-icon="mdi-paperclip"
          outlined
          :show-size="1000"
          :background-color="isDragging ? 'blue' : 'null'"
        >
          <template v-slot:selection="{ index, text }">
            <v-chip
              v-if="index < 2"
              color="deep-purple accent-4"
              dark
              label
              small
              >{{ text }}</v-chip
            >
            <span
              v-else-if="index === 2"
              class="overline grey--text text--darken-3 mx-2"
              >+{{ files.length - 2 }} File(s)</span
            >
          </template>
        </v-file-input>
      </v-row>
    </v-card>
  </v-app>
</template>

<script>
// import { createBaseApiClient } from '@/api/apiBase'

export default {
  // name: 'DragAndDrop',

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
