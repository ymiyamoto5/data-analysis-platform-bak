<template>
  <v-app>
    <v-container class="mt-6 mb-6">
      <v-row dense>
        <v-col cols="5">
          <ModelSelect
            @selectInput="setModel"
            @textInput="setContainerName"
          ></ModelSelect>
        </v-col>
      </v-row>
      <v-row justify="center">
        <v-btn
          color="primary"
          @click="createContainer"
          :disabled="running || !modelSelected"
          :loading="running"
          >コンテナ作成</v-btn
        >
      </v-row>
    </v-container>
    <v-divider></v-divider>
    <v-container class="mt-6 ">
      <v-row>
        <ContainerManager
          :containers="containers"
          @updateState="fetchContainers"
        ></ContainerManager>
      </v-row>
    </v-container>
  </v-app>
</template>

<script>
import { createBaseApiClient } from '@/api/apiBase'
import ModelSelect from '@/components/ServingModel/ModelSelect.vue'
import ContainerManager from '@/components/ServingModel/ContainerManager.vue'

const CREATE_CONTAINER_API_URL = '/api/v1/models/container'
const CONTAINER_API_URL = '/api/v1/models/containers'

export default {
  components: {
    ModelSelect,
    ContainerManager,
  },
  data() {
    return {
      dataSelected: false,
      running: false,
      machineId: '',
      targetDir: '',
      model: '',
      version: '',
      containerName: '',
      modelSelected: false,
      alert: false,
      alertMessage: '',
      containers: [],
    }
  },
  mounted() {
    this.fetchContainers()
  },
  methods: {
    setModel(value) {
      this.model = value['model']
      this.version = value['version']
      this.modelSelected = !!this.version && !!this.containerName
    },
    setContainerName(value) {
      this.containerName = value
      this.modelSelected = !!value && !!this.version
    },
    // ショット切り出し開始
    createContainer: async function() {
      this.running = true

      const postData = {
        model: this.model,
        version: this.version,
        tag_name: this.containerName,
      }
      const client = createBaseApiClient()
      await client
        .post(CREATE_CONTAINER_API_URL, postData)
        .then(() => {
          this.running = false
          this.fetchContainers()
        })
        .catch((e) => {
          console.log(e.response.data.detail)
        })
    },
    fetchContainers: async function() {
      const client = createBaseApiClient()
      await client
        .get(CONTAINER_API_URL)
        .then((res) => {
          this.containers = res.data.data
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
