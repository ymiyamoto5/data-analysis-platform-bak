<template>
  <v-container>
    <v-row>
      <v-slider
        v-model="value"
        vertical
        hide-details
        min="-2"
        max="2"
        height="300px"
        dense
        step="0.1"
        class="align-center"
        @input="$emit('input', $event)"
      ></v-slider>
    </v-row>
  </v-container>
</template>

<script>
export default {
  props: ['targetDateStr'],
  watch: {
    targetDateStr: function() {
      // TODO: 対象に応じて動的に設定
      console.log()
    },
  },
  data() {
    return {
      value: 0,
    }
  },
}
</script>
