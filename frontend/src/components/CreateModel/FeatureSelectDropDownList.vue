<template>
  <container>
    <v-select
      class="select"
      :items="features"
      label="特徴量"
      outlined
      dense
      @input="$emit('setFeature', $event)"
    ></v-select>
  </container>
</template>

<script>
export default {
  props: ['features'],
}
</script>

<style scoped>
.select {
  width: 250px;
}
</style>
