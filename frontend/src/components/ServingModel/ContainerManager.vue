<template>
  <v-app>
    <v-container>
      <v-expansion-panels>
        <v-expansion-panel
          v-for="(container, index) in attribute"
          :key="container.image"
          class="mb-3"
        >
          <v-expansion-panel-header>
            <v-row no-gutters>
              <v-col cols="8">
                {{ containerName(container.image) }}
              </v-col>
            </v-row>
          </v-expansion-panel-header>
          <v-expansion-panel-content>
            <v-row>
              <v-col cols="4">
                <v-text-field
                  v-model="container.port"
                  :ref="container.image"
                  label="ポート番号"
                  type="number"
                  :rules="container.state == 'stopping' ? rules : norules"
                  :disabled="container.state != 'stopping'"
                  @input="setPortNumber(index, $event)"
                ></v-text-field>
              </v-col>
            </v-row>
            <v-row class="mb-3">
              <v-btn
                :disabled="portValidate(container.image)"
                :color="container.color"
                class="mr-3"
                @click="containerStateChange(index)"
              >
                {{ container.label }}
              </v-btn>
              <v-btn
                v-if="container.delete"
                color="error"
                @click="deleteContainer(index)"
              >
                削除
              </v-btn>
            </v-row>
          </v-expansion-panel-content>
        </v-expansion-panel>
      </v-expansion-panels>
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
const CONTAINER_API_URL = '/api/v1/models/container/'
const CONTAINER_PORT_API_URL = CONTAINER_API_URL + 'ports'
const CONTAINER_RUN_API_URL = CONTAINER_API_URL + 'run/'
const CONTAINER_STOP_API_URL = CONTAINER_API_URL + 'stop/'

export default {
  props: ['containers'],
  data() {
    return {
      bindedPorts: [],
      attribute: this.containers.map(this.makeAttribute),
      rules: [
        (value) => !this.bindedPorts.includes(value) || 'ポート使用中',
        (value) =>
          !Object.values(this.servicePorts).includes(Number(value)) ||
          'ポート使用中',
        (value) =>
          !value || (value > 1023 && value < 65536) || '使用不可ポート',
      ],
      norules: [true],
      servicePorts: {
        mlflow: 5000,
        kibana: 5601,
        fastapiDev: 8000,
        vueDev: 8888,
        minio0: 9000,
        minio1: 9001,
        elasticsearch: 9200,
      },
      snackbar: false,
      snackbarMessage: '',
    }
  },
  computed: {
    containerName: function() {
      return function(name) {
        const regex = /serving-model_(.*):.*/
        const res = name.match(regex)
        return res.slice(-1)[0]
      }
    },
    portValidate: function() {
      return function(image) {
        if (this.$refs[image]) {
          return !this.$refs[image][0].validate()
        } else {
          return false
        }
      }
    },
  },
  watch: {
    containers: function(newContainers) {
      this.attribute = newContainers.map(this.makeAttribute)
    },
  },
  mounted() {
    this.fetchBindedPorts()
  },
  methods: {
    errorSnackbar(message) {
      this.$store.commit('setShowErrorSnackbar', true)
      this.$store.commit('setErrorHeader', message.statusText)
      this.$store.commit('setErrorMsg', message.data.detail)
    },
    makeAttribute(container) {
      return {
        image: container.image,
        state: container.state,
        name: container.name,
        port: container.port,
        color: container.state == 'stopping' ? 'primary' : 'error',
        label: container.state == 'stopping' ? '起動' : '停止',
        delete: container.state == 'stopping' ? true : false,
      }
    },
    setButtonLabel(container) {
      return container.state == 'stopping' ? '起動' : '停止'
    },
    setButtonColor(container) {
      return container.state == 'stopping' ? 'primary' : 'error'
    },
    setPortNumber(index, value) {
      this.containers[index].port = value
    },
    fetchBindedPorts: async function() {
      const client = createBaseApiClient()
      await client
        .get(CONTAINER_PORT_API_URL)
        .then((res) => {
          if (res.data.length === 0) {
            return
          }
          this.bindedPorts = res.data.binded
        })
        .catch((e) => {
          console.log(e.response)
          this.errorSnackbar(e.response)
        })
    },
    containerStateChange: async function(index) {
      let request = ''
      let message = ''
      if (this.containers[index].state == 'stopping') {
        request =
          CONTAINER_RUN_API_URL +
          this.containers[index].image +
          '/' +
          this.containers[index].port
        message = 'コンテナを起動しました'
      } else {
        request = CONTAINER_STOP_API_URL + this.containers[index].name
        message = 'コンテナを停止しました'
      }

      const client = createBaseApiClient()
      await client
        .put(request)
        .then((res) => {
          if (res.data.length === 0) {
            return
          }
          this.containers[index] = res.data.data
          this.attribute = this.containers.map(this.makeAttribute)
          this.fetchBindedPorts()
          this.snackbarMessage = message
          this.snackbar = true
        })
        .catch((e) => {
          console.log(e.response)
          this.errorSnackbar(e.response)
        })
    },
    deleteContainer: async function(index) {
      const client = createBaseApiClient()
      await client
        .delete(CONTAINER_API_URL + this.containers[index].image)
        .then((res) => {
          if (res.data.length === 0) {
            return
          }
          this.containers.splice(index, 1)
          this.snackbarMessage = 'コンテナを削除しました'
          this.snackbar = true
        })
        .catch((e) => {
          console.log(e.response)
          this.errorSnackbar(e.response)
        })
    },
  },
}
</script>
