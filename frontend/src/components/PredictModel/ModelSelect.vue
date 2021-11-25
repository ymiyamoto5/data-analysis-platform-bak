<template>
  <v-container>
    <v-select
      class="select"
      :items="models"
      label="モデル"
      outlined
      dense
      @input="setModel"
    ></v-select>
    <v-select
      class="select"
      v-model="selectedVersion"
      :items="versions"
      label="バージョン"
      outlined
      dense
      @change="
        $emit('selectInput', {
          model: selectedModel,
          version: $event,
        })
      "
    ></v-select>
  </v-container>
</template>

<script>
import { createBaseApiClient } from '@/api/apiBase'
const MODELS_API_URL = '/api/v1/models/'
const MODEL_VERSIONS_API_URL = '/api/v1/models/versions'

export default {
  data() {
    return {
      models: [],
      selectedModel: '',
      versions: [],
      selectedVersion: '',
    }
  },
  watch: {
    selectedModel: function() {
      this.fetchVersions()
    },
  },
  mounted() {
    this.fetchModels()
  },
  methods: {
    errorSnackbar(message) {
      this.$store.commit('setShowErrorSnackbar', true)
      this.$store.commit('setErrorHeader', message.statusText)
      this.$store.commit('setErrorMsg', message.data.detail)
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
          this.selectedVersion = ''
          this.$emit('selectInput', {
            model: this.selectedModel,
            version: '',
          })
          this.versions = res.data
        })
        .catch((e) => {
          console.log(e.response.data.detail)
          this.errorSnackbar(e.response)
        })
    },
  },
}
</script>

<style scoped>
.select {
  width: 250px;
}
</style>
