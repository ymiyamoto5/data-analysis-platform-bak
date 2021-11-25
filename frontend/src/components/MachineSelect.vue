<template>
  <v-select
    class="select"
    :items="machines"
    label="機器"
    outlined
    dense
    @input="$emit('input', $event)"
  ></v-select>
</template>

<script>
import { createBaseApiClient } from '@/api/apiBase'
const MACHINES_API_URL = '/api/v1/machines/'

export default {
  data() {
    return {
      machines: [],
    }
  },
  mounted() {
    this.fetchMachines()
  },
  methods: {
    errorSnackbar(message) {
      this.$store.commit('setShowErrorSnackbar', true)
      this.$store.commit('setErrorHeader', message.statusText)
      this.$store.commit('setErrorMsg', message.data.detail)
    },
    fetchMachines: async function() {
      const client = createBaseApiClient()
      await client
        .get(MACHINES_API_URL)
        .then((res) => {
          if (res.data.length === 0) {
            return
          }
          this.machines = res.data.map((x) => x.machine_id)
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
