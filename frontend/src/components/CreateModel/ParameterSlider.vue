<template>
  <v-card flat color="transparent">
    <v-card-text>
      <v-slider
        v-for="param in params"
        :key="param.name"
        :label="param.name"
        v-model="value[param.name]"
        :max="param.max"
        :min="param.min"
        hide-details
        :step="param.step"
        class="align-center"
        @input="$emit('input', $event, param.name)"
      >
        <template v-slot:append>
          <v-text-field
            v-model="value[param.name]"
            class="mt-0 pt-0"
            hide-details
            single-line
            type="number"
            style="width: 60px"
          ></v-text-field>
        </template>
      </v-slider>
    </v-card-text>
  </v-card>
</template>

<script>
import { createBaseApiClient } from '@/api/apiBase'
const ALGORITHM_API_URL = '/api/v1/models/algorithm/'

export default {
  props: ['algorithm'],
  data() {
    return {
      params: [],
      value: {},
    }
  },
  mounted() {
    this.fetchAlgorithms()
  },
  methods: {
    fetchAlgorithms: async function() {
      const client = createBaseApiClient()
      await client
        .get(ALGORITHM_API_URL + this.algorithm)
        .then((res) => {
          if (res.data.length === 0) {
            return
          }
          this.params = res.data.params
          this.value[res.data.params.name] = this.params.min
        })
        .catch((e) => {
          console.log(e)
        })
    },
  },
}
</script>
