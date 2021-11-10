<template>
  <v-app>
    <v-container class="mt-6 mb-6">
      <v-row dense>
        <v-col cols="5">
          <ModelSelect @selectInput="setModel"></ModelSelect>
        </v-col>
      </v-row>
      <v-row dense>
        <v-col cols="8">
          <DataSelect @input="setDataset"></DataSelect>
        </v-col>
      </v-row>
      <v-row justify="center">
        <v-btn
          color="primary"
          @click="predict"
          :disabled="running || !modelSelected || !dataSelected"
          :loading="running"
          >予測</v-btn
        >
      </v-row>
    </v-container>
    <v-snackbar
      v-model="snackbar"
      timeout="5000"
      top
      color="success"
      style="white-space: pre;"
    >
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
import ModelSelect from '@/components/PredictModel/ModelSelect.vue'
import DataSelect from '@/components/PredictModel/DataSelect.vue'

const PREDICT_API_URL = '/api/v1/models/predict'

export default {
  components: {
    ModelSelect,
    DataSelect,
  },
  data() {
    return {
      running: false,
      machineId: '',
      targetDir: '',
      model: '',
      version: '',
      modelSelected: false,
      dataSelected: false,
      data: [],
      label: [],
      snackbar: false,
      snackbarMessage: '',
    }
  },
  methods: {
    setModel(value) {
      this.model = value['model']
      this.version = value['version']
      this.modelSelected = !!this.version
    },
    setDataset(value) {
      this.machineId = value['machine']
      this.targetDir = value['target']
      this.shot = value['shot']
      this.dataSelected = !!this.shot
    },
    predict: async function() {
      this.running = true

      const postData = {
        model: this.model,
        version: this.version,
        machine_id: this.machineId,
        target_dir: this.targetDir,
        shot: this.shot,
      }
      const client = createBaseApiClient()
      await client
        .post(PREDICT_API_URL, postData)
        .then((res) => {
          this.running = false
          this.data = res.data.data
          this.label = res.data.label
          this.snackbarMessage = `予測が完了しました\n 予測結果:${this.label}`
          this.snackbar = true
        })
        .catch((e) => {
          console.log(e.response.data.detail)
        })
    },
  },
}
</script>

<style scoped>
/* #prev {
  margin-top: 200px;
}
#next {
  margin-top: 200px;
} */
</style>
