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
  data() {
    return {
      min: 0,
      max: 100,
      range: [100, 0],
    }
  },
}
</script>
