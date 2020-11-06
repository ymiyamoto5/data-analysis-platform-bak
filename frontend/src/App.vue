<template>
  <div id="app">
    <NavigationBar />
    <v-app>
      <router-view></router-view>
    </v-app>
  </div>
</template>

<script lang="ts">
import Vue from 'vue';
import NavigationBar from './components/NavigationBar.vue'

export default Vue.extend({
  name: 'App',

  components: {
    NavigationBar
  },
});
</script>
