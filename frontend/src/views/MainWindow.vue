<template>
  <v-app id="inspire">
    <v-navigation-drawer
      v-model="drawer"
      app
      class="pt-4"
      color="blue"
      mini-variant
    >
      <v-icon large dark>mdi-home</v-icon>
      <v-icon large dark>mdi-history</v-icon>
      <v-icon large dark>mdi-cog-outline</v-icon>
    </v-navigation-drawer>

    <v-main id="v-main">
      <div id="page-title">
        <p class="text-h5">データ収集</p>
      </div>
      <DataCollect />
    </v-main>
  </v-app>
</template>

<script>
import DataCollect from '@/views/DataCollect.vue'

export default {
  name: 'main-window',
  components: {
    DataCollect,
  },
  data() {
    return {
      drawer: {},
    }
  },
}
</script>

<style scoped>
#v-main {
  margin: 10px;
  padding: 10px;
}

#page-title {
  margin: 10px;
}

.v-icon {
  margin-left: 10px;
  margin-top: 15px;
  margin-bottom: 15px;
}
</style>
