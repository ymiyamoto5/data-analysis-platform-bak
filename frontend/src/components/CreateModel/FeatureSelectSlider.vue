<template>
  <container>
    <v-select
      class="select"
      :items="features"
      label="特徴量"
      outlined
      dense
      @input="$emit('nof', $event)"
    ></v-select>
  </container>
</template>

<script>
export default {
  props: ['features'],
}
</script>
