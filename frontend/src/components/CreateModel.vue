<template>
  <v-app>
    <v-container class="mt-6">
      <v-row dense>
        <v-col cols="5">
          <FeatureSelect @input="setFeature"></FeatureSelect>
        </v-col>
      </v-row>
      <v-row dense>
        <v-col cols="9">
          <ChartCard
            :machineId="machineId"
            :targetDir="targetDir"
            :feature="feature"
            @setFeatures="features = $event"
          />
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="9">
          <FeatureSelectDropDownList
            v-if="dataSelected"
            :features="features"
            @setFeature="feature = $event"
          ></FeatureSelectDropDownList>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="5">
          <AlgorithmSelect
            v-if="dataSelected"
            @input="setAlgorithm"
          ></AlgorithmSelect>
        </v-col>
      </v-row>
      <v-row dense>
        <v-col cols="9">
          <ParameterSlider
            v-if="algorithmSelected"
            @input="setParameter"
            :algorithm="algorithm"
          ></ParameterSlider>
        </v-col>
      </v-row>
      <v-row justify="center" v-if="dataSelected">
        <v-btn
          color="primary"
          @click="createModel"
          :disabled="running || !algorithmSelected"
          :loading="running"
          >モデル作成</v-btn
        >
      </v-row>
    </v-container>
    <v-snackbar v-model="snackbar" timeout="5000" top color="success">
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
import FeatureSelect from '@/components/CreateModel/FeatureSelect.vue'
import ChartCard from '@/components/CreateModel/ChartCard.vue'
import FeatureSelectDropDownList from '@/components/CreateModel/FeatureSelectDropDownList.vue'
import AlgorithmSelect from '@/components/CreateModel/AlgorithmSelect.vue'
import ParameterSlider from '@/components/CreateModel/ParameterSlider.vue'

const CREATE_MODEL_API_URL = '/api/v1/models/'

export default {
  components: {
    FeatureSelect,
    FeatureSelectDropDownList,
    ChartCard,
    AlgorithmSelect,
    ParameterSlider,
  },
  data() {
    return {
      dataSelected: false,
      running: false,
      machineId: '',
      targetDir: '',
      collectData: '',
      features: [],
      feature: '',
      algorithmSelected: false,
      algorithm: '',
      params: {},
      snackbar: false,
      snackbarMessage: '',
    }
  },
  methods: {
    errorSnackbar(message) {
      this.$store.commit('setShowErrorSnackbar', true)
      this.$store.commit('setErrorHeader', message.statusText)
      this.$store.commit('setErrorMsg', message.data.detail)
    },
    setFeature(value) {
      this.machineId = value[0]
      this.targetDir = value[1]
      this.dataSelected = true
    },
    setAlgorithm(value) {
      this.algorithm = value
      this.algorithmSelected = true
    },
    setParameter(value, key) {
      this.params[key] = value
    },
    createModel: async function() {
      this.running = true

      const postData = {
        machine_id: this.machineId,
        target_dir: this.targetDir,
        algorithm: this.algorithm,
        params: this.params,
      }
      const client = createBaseApiClient()
      await client
        .post(CREATE_MODEL_API_URL, postData)
        .then(() => {
          this.running = false
          this.snackbarMessage = 'モデルの作成が完了しました'
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

<style scoped>
/* #prev {
  margin-top: 200px;
}
#next {
  margin-top: 200px;
} */
</style>
