<template>
  <v-card flat color="transparent">
    <v-card-text>
      <v-range-slider
        v-model="range"
        :max="max"
        :min="min"
        hide-details
        height="300px"
        vertical
        dense
        step="0.1"
        class="align-center"
        @input="$emit('input', $event)"
      >
        <template v-slot:prepend>
          <v-text-field
            :value="range[0]"
            class="mt-0 pt-0"
            hide-details
            single-line
            type="number"
            style="width: 60px"
            @change="$set(range, 0, $event)"
          ></v-text-field>
        </template>
        <template v-slot:append>
          <v-text-field
            :value="range[1]"
            class="mt-0 pt-0"
            hide-details
            single-line
            type="number"
            style="width: 60px"
            @change="$set(range, 1, $event)"
          ></v-text-field>
        </template>
      </v-range-slider>
    </v-card-text>
  </v-card>
</template>

<script>
export default {
  props: ['targetDateStr', 'maxStrokeDisplacement', 'minStrokeDisplacement'],
  watch: {
    targetDateStr: function() {
      // TODO: 対象に応じて動的に設定
      console.log()
    },
    minStrokeDisplacement(val) {
      this.min = val
      this.$set(this.range, 1, val)
    },
    maxStrokeDisplacement(val) {
      this.max = val
      this.$set(this.range, 0, val)
    },
  },
  data() {
    return {
      min: 0, // しきい値スライダーの最小値
      max: 0, // しきい値スライダーの最大値
      range: [0, 0], // しきい値の範囲 [start_displacement, end_displacement]
    }
  },
}
</script>
