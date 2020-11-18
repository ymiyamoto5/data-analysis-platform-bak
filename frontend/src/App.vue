<template>
  <div id="app">
    <v-app>
      <Manager></Manager>
    </v-app>
  </div>
</template>

<script lang="ts">
import Vue from 'vue';
import Manager from './views/Manager.vue'

export default Vue.extend({
  name: 'App',

  components: {
    Manager
  },
});
</script>
