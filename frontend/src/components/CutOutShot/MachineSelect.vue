<template>
  <v-select
    class="select"
    :items="items"
    label="機器"
    outlined
    dense
    @input="$emit('input', $event)"
  ></v-select>
</template>

<script>
import { createBaseApiClient } from '@/api/apiBase'
const MACHINES_API_URL = '/api/v1/machines'

export default {
  data() {
    return {
      items: [],
    }
  },
  mounted() {
    this.fetchMachines()
  },
  methods: {
    fetchMachines: async function() {
      const client = createBaseApiClient()
      await client
        .get(MACHINES_API_URL)
        .then((res) => {
          if (res.data.length === 0) {
            return
          }
          this.items = res.data.map((x) => x.machine_id)
        })
        .catch((e) => {
          console.log(e.response.data.message)
          this.errorDialog(e.response.data.message)
        })
    },
  },
}
</script>

<style scoped>
.select {
  width: 200px;
}
</style>
