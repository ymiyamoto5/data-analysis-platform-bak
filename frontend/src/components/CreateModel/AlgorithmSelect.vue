<template>
  <v-select
    class="select"
    :items="algorithms"
    label="機械学習アルゴリズム"
    outlined
    dense
    @input="$emit('input', $event)"
  ></v-select>
</template>

<script>
import { createBaseApiClient } from '@/api/apiBase'
const ALGORITHM_API_URL = '/api/v1/models/algorithm'

export default {
  data() {
    return {
      algorithms: [],
    }
  },
  mounted() {
    this.fetchAlgorithms()
  },
  methods: {
    errorSnackbar(message) {
      this.$store.commit('setShowErrorSnackbar', true)
      this.$store.commit('setErrorHeader', message.statusText)
      this.$store.commit('setErrorMsg', message.data.detail)
    },
    fetchAlgorithms: async function() {
      const client = createBaseApiClient()
      await client
        .get(ALGORITHM_API_URL)
        .then((res) => {
          if (res.data.length === 0) {
            return
          }
          this.algorithms = res.data.map((x) => x.algorithm_name)
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
